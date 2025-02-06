#! /usr/bin/env python
#load binary lib/pyeudaq.so

import time
import argparse
from src.bdaq_supply import PowerManager
# from standalone_power import CHWrapper
import pyeudaq



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

    def __del__(self):
        if self.power_mng:
            self.power_mng.shutdown()

    def handle_error(self, error):
        print(f"Error occurred: {error}")
        if self.power_mng:
            self.power_mng.shutdown()

    def DoInitialise(self):
        try:
            self.ini = self.GetInitConfiguration()
            self.power_mng = PowerManager(self.ini.Get('SERIAL_PORT'), bias=0, hv=0)
            self.power_mng.init()
        except Exception as e:
            self.handle_error(e)
            raise

    def DoConfigure(self):
        try:
            self.conf = self.GetConfiguration()
            tmp = self.conf.Get('BIAS')  # voltage 'BIAS', Ch2
            bias = 0.0
            if tmp:
                bias = float(tmp.replace(',', '.'))
            tmp = self.conf.Get('HV')  # voltage 'HV', Ch3
            hv = 0.0
            if tmp:
                hv = float(tmp.replace(',', '.'))
            self.power_cycle_at_stop = int(self.conf.as_dict().get('POWER_CYCLE_AT_STOP',0))
            self.power_mng.bias=bias
            self.power_mng.hv=hv
            self.is_running = 1
            self.power_mng.configure()
        except Exception as e:
            self.handle_error(e)
            raise

    def DoStartRun(self):
        try:
            if self.power_cycle_at_stop == True and self.power_mng.ps.allOff():
                self.power_mng.startup()
            elif self.power_mng.ch_bias.measVoltage() == 0 and self.power_mng.ch_hv.measVoltage() == 0:
                self.power_mng.rampUp()
            
        except Exception as e:
            self.handle_error(e)
            raise

    def DoStopRun(self):
        try:
            if self.power_cycle_at_stop == True and self.power_mng:
                self.power_mng.shutdown()
                self.power_mng.startup()
            elif self.power_mng:
                self.power_mng.rampDown()
            self.is_running = False
        except Exception as e:
            self.handle_error(e)
            raise

    def DoReset(self):
        try:
            self.is_running = False
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
            if self.power_mng:
                self.power_mng.shutdown()
        except Exception as e:
            self.handle_error(e)
            raise
     
    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        if self.power_mng:
            self.power_mng.shutdown()
   


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

