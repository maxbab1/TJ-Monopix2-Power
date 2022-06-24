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

class HamekProducer(pyeudaq.Producer):
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

    def DoConfigure(self):
        self.conf = self.GetConfiguration()

        tmp = self.conf.Get('BIAS')
        bias = 0.0
        if tmp:
            bias = float(tmp)
        tmp = self.conf.Get('HV')
        hv = 0.0
        if tmp:
            hv = float(tmp)

        self.power_mng = PowerManager(self.conf.Get('SERIAL_PORT'), bias, hv)

        self.channels.append(CHWrapper("CH1: BDAQ53 Board", self.power_mng.ch_bdaq))
        self.channels.append(CHWrapper("CH2: PSUB/PWELL", self.power_mng.ch_bias))
        self.channels.append(CHWrapper("CH3: HV", self.power_mng.ch_hv))
        self.channels.append(CHWrapper("CH4: LV supply", self.power_mng.ch_chip))

    def DoStartRun(self):
        self.is_running = 1
        self.power_mng.startup()

        
    def DoStopRun(self):
        self.is_running = 0
        self.power_mng.shutdown()

    def DoReset(self):
        self.is_running = 0
        if self.power_mng:
            self.power_mng.shutdown()

    def RunLoop(self):
        while self.is_running:
            for ch in self.channels:
                if self.is_running:
                    self.SetStatusTag(ch.name, ch.info())
            time.sleep(1)

    def DoTerminate(self):
        if self.power_mng:
            self.power_mng.shutdown()
            time.sleep(3)  # block until finished powering off


if __name__ == '__main__':
    # Parse program arguments
    description = 'Start EUDAQ producer for Hamek PS'
    parser = argparse.ArgumentParser(prog='hamek_producer',
                                     description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-r', metavar='address',
                        help='Destination address',
                        default='tcp://localhost:44000',
                        nargs='?')

    args = parser.parse_args()

    producer = HamekProducer('hamek', args.r)
    print('connecting to runcontrol in ', args.r)
    producer.Connect()
    time.sleep(2)
    while producer.IsConnected():
        time.sleep(1)
