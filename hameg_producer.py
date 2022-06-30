#! /usr/bin/env python
# load binary lib/pyeudaq.so

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

    def __del__(self):
        if self.power_mng:
            self.power_mng.shutdown()

    def DoInitialise(self):
        self.ini = self.GetInitConfiguration()
        # actually no init items needed, store for possible future uses

    def DoConfigure(self):
        self.conf = self.GetConfiguration()

        #  TODO: generalize me, use Ch1, ..., Ch4 instead of Monopix2 voltage
        #   names, maybe also make current and slope configurable
        tmp = self.conf.Get('BIAS')  # voltage 'BIAS', Ch2
        bias = 0.0
        if tmp:
            bias = float(tmp.replace(',', '.'))
        tmp = self.conf.Get('HV')  # voltage 'HV', Ch3
        hv = 0.0
        if tmp:
            hv = float(tmp.replace(',', '.'))

        self.power_mng = PowerManager(self.conf.Get('SERIAL_PORT'), bias, hv)

        self.channels.append(CHWrapper("CH1: BDAQ53 Board", self.power_mng.ch_bdaq))
        self.channels.append(CHWrapper("CH2: PSUB/PWELL", self.power_mng.ch_bias))
        self.channels.append(CHWrapper("CH3: HV", self.power_mng.ch_hv))
        self.channels.append(CHWrapper("CH4: LV supply", self.power_mng.ch_chip))
        
        self.is_running = 1
        self.power_mng.startup()
        

    def DoStartRun(self):
    	pass

        
    def DoStopRun(self):
        self.is_running = 0
        self.power_mng.shutdown()

    def DoReset(self):
        self.is_running = 0
        if self.power_mng:
            self.power_mng.shutdown()

    def RunLoop(self):
        return
        while self.is_running:
            for ch in self.channels:
                if self.is_running:
                    self.SetStatusTag(ch.name, ch.info())
                    # we do not send any events, just updating the status with current voltage and current per ch
            time.sleep(1)

    def DoTerminate(self):
        if self.power_mng:
            self.power_mng.shutdown()
            time.sleep(3)  # block until finished powering off


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
    producer.Connect()
    time.sleep(2)
    while producer.IsConnected():
        time.sleep(1)
