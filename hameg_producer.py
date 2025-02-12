#! /usr/bin/env python
#load binary lib/pyeudaq.so

import time
import datetime
import argparse
from src.bdaq_supply import PowerManager
# from standalone_power import CHWrapper
import pyeudaq
import threading
import csv



class CHWrapper:
    def __init__(self, name, channel):
        self.ch = channel
        self.name = name
        self.measure()

    def measure(self):
        self.u = self.ch.measVoltage()
        self.i = self.ch.measCurrent()

    def print(self):
        print(self.name + ":")
        print("      {:4.2f} V".format(self.u))
        print("    {:5.1f} mA".format(self.i * 1e3))
        print("")

    def info(self):
        self.measure()
        return f'{self.u} V {self.i * 1e3} mA'



class HamegProducer(pyeudaq.Producer):
    def __init__(self, name, runctrl):
        pyeudaq.Producer.__init__(self, name, runctrl)
        self.is_running = 0
        self.ini = None
        self.conf = None
        self.power_mng = None
        self.channels = []
        self.power_cycle_at_stop = 0
        self.run_number = None
        self.log_file = "power_log.csv" # Default; will be updated in DoStartRun
        self.log_interval = 10
        self.logging_enabled = False
        self.thread_logging = None
        self.logging_directory = "/home/silicon/TJ-Monopix2/TJ-Monopix2-Power/Log"

    def __del__(self):
        if self.power_mng:
            self.power_mng.shutdown()
        if self.thread_logging:
            self.thread_logging.join()

    def handle_error(self, error):
        print(f"Error occurred: {error}")
        if self.power_mng:
            self.power_mng.shutdown()
        if self.thread_logging:
            self.is_running = 0
            self.thread_logging.join()

    def DoInitialise(self):
        try:
            self.ini = self.GetInitConfiguration()
            self.power_mng = PowerManager(self.ini.Get('serial_port'), bias=0, hv=0)
            self.power_mng.init()
        except Exception as e:
            self.handle_error(e)
            raise

    def DoConfigure(self):
        try:
            self.conf = self.GetConfiguration().as_dict()
            self.logging_enabled = int(self.conf.get("logging", 0)) == 1
            if self.logging_enabled:
                self.log_interval = int(self.conf.get("log_interval", 10))
                self.logging_directory=self.conf.get("logging_directory","/home/silicon/TJ-Monopix2/TJ-Monopix2-Power/Log")

            tmp = self.conf.get('bias',None)  # voltage 'BIAS', Ch2
            bias = 0.0
            if tmp:
                bias = float(tmp.replace(',', '.'))
            tmp = self.conf.get('hv',None)  # voltage 'HV', Ch3
            hv = 0.0
            if tmp:
                hv = float(tmp.replace(',', '.'))
            self.power_cycle_at_stop = int(self.conf.get('power_cycle_at_stop',0))
            self.power_mng.bias=bias
            self.power_mng.hv=hv
            self.power_mng.configure()
        except Exception as e:
            self.handle_error(e)
            raise

    def DoStartRun(self):
        try:
            self.is_running = 1
            if self.power_cycle_at_stop == True and self.power_mng.ps.allOff():
                self.power_mng.startup()
            elif self.power_mng.ch_bias.measVoltage() == 0 and self.power_mng.ch_hv.measVoltage() == 0:
                self.power_mng.rampUp()

            if self.logging_enabled:
                self.run_number = self.GetRunNumber()
                self.log_file = f"power_log_run{self.run_number}.csv"
                self.thread_logging = threading.Thread(target=self.log_power_data)
                self.thread_logging.start()
            
        except Exception as e:
            self.handle_error(e)
            raise

    def DoStopRun(self):
        try:
            self.is_running = 0
            if self.thread_logging:
                    self.thread_logging.join()
            if self.power_cycle_at_stop == True and self.power_mng:
                self.power_mng.shutdown()
                self.power_mng.startup()
                self.is_running = 1
            elif self.power_mng:

                self.power_mng.rampDown()
            
        except Exception as e:
            self.handle_error(e)
            raise

    def DoReset(self):
        try:
            self.is_running = False
            if self.thread_logging:
                self.is_running = 0
                self.thread_logging.join()
            if self.power_mng:
                self.power_mng.shutdown()
        except Exception as e:
            self.handle_error(e)
            raise

    def RunLoop(self):
        return
        try:
            while self.is_running:
                # Example: Status monitoring (if needed)
                time.sleep(1)
        except Exception as e:
            self.handle_error(e)
            raise

    def DoTerminate(self):
        try:
            if self.thread_logging:
                self.is_running = 0
                self.thread_logging.join()
            if self.power_mng:
                self.power_mng.shutdown()
           
        except Exception as e:
            self.handle_error(e)
            raise
     
    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        if self.thread_logging:
            self.is_running = 0
            self.thread_logging.join()
        if self.power_mng:
            self.power_mng.shutdown()
        
   
    def log_power_data(self):
        """ Logs power supply data to a CSV file at a set interval. """
        try:
            with open(self.logging_directory+"/"+self.log_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "BDAQ53 Board Current (mA)", "PSUB/PWELL Current (mA)", "HV Current (mA)", "LV supply (mA)"])

                while self.is_running:
                    bdaq = self.power_mng.ch_bdaq.measCurrent()*1e3
                    bias = self.power_mng.ch_bias.measCurrent()*1e3
                    hv = self.power_mng.ch_hv.measCurrent()*1e3
                    chip = self.power_mng.ch_chip.measCurrent()*1e3
                   

                    writer.writerow([datetime.datetime.now(), bdaq, bias, hv, chip])
                    file.flush()
                    time.sleep(self.log_interval)

        except Exception as e:
            self.handle_error(e)
            raise

if __name__ == '__main__':
    # Parse program arguments
    description = 'EUDAQ producer for Hameg-PS'
    parser = argparse.ArgumentParser(prog='Hameg_producer',
                                     description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-r', metavar='address',
                        help='Destination address',
                        default='tcp://localhost:44000')
    parser.add_argument('-n', metavar='name',
                        help='Producer name',
                        default='hameg')

    args = parser.parse_args()

    producer = HamegProducer(args.n, args.r)
    print(f'producer {args.n} connecting to runcontrol in {args.r}')
    with producer as p:
        p.Connect()
        time.sleep(2)
        while p.IsConnected():
            time.sleep(1)

