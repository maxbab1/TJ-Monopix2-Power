from src.HMP4040 import HMP4040
import time
import os
import numpy as np
 



class PowerManager():
    def __init__(self, serial, bias, hv):
        self.ps = HMP4040(port=serial)
        self.bias = bias
        self.hv = hv
        
        self.ch_bdaq = self.ps.out1   # supply for the bdaq board
        self.ch_chip = self.ps.out4   # supply for the chip (digital)
        
        self.ch_bias = self.ps.out2   # supply for the Bias supply
        self.ch_hv   = self.ps.out3   # supply for the HV supply
    
    def __enter__(self):
        self.startup()
        return self
    
    def __exit__(self, a, b, c):
        self.shutdown()
    
    
    def init(self):
        if not self.ps.allOff():
            print("WARNING: not all supplies were switched off!")
            self.shutdown(before=True)
            time.sleep(0.5)

        self.ps.reset()
        self.ch_chip.setVoltage(1.8)
        self.ch_chip.setCurrent(2.5)
        self.ch_chip.setFuse(delay=50)
        
        self.ch_bdaq.setVoltage(5.0)
        self.ch_bdaq.setCurrent(2.0)
        self.ch_bdaq.setFuse(delay=50)
        self.ch_chip.linkFuse(self.ch_bdaq.ch)
        
        self.ch_bias.setVoltage(0.0)
        self.ch_bias.setCurrent(0.008)
        self.ch_bias.setFuse(delay=50)
        self.ch_bias.linkFuse(self.ch_bdaq.ch)
        self.ch_bias.linkFuse(self.ch_chip.ch)
        self.ch_chip.linkFuse(self.ch_bias.ch)
        
        self.ch_hv.setVoltage(0.0)
        self.ch_hv.setCurrent(0.008)
        self.ch_hv.setFuse(delay=50)
        self.ch_hv.linkFuse(self.ch_bdaq.ch)
        self.ch_hv.linkFuse(self.ch_chip.ch)
        self.ch_chip.linkFuse(self.ch_hv.ch)
        
        self.ch_bias.setOn(True)
        self.ch_hv.setOn(True)
        time.sleep(0.1)
        self.ch_chip.setOn(True)
        time.sleep(0.1)
        self.ch_bdaq.setOn(True)

    
    def configure(self):
        if self.ps.allOff():
            self.init()
        #if self.ch_bias.measVoltage() != 0 or self.ch_hv.measVoltage() !=0:
         #   self.shutdown()
          #  self.init()
        self.rampUp()
        print("Power is up!")

    def startup(self):
        self.init()
        self.configure()
    
        #time.sleep(0.5)
        #print("Power is up, waiting for ping response...", end='', flush=True)
        #for i in range(20):
        #    time.sleep(1.1)
        #    if os.system("ping -c 1 192.168.10.23 -t 1 > /dev/null") == 0:
        #        print(" [ OK ]\n Connection to bdaq board ready now!")
        #        break
    
    
    """ disable all power supply rails in order - may be called with before==True at beginning 
    of script if at least one output was not disabled before (e.g. after a crash) """
    def shutdown(self, before=False):
        if not before:
            print("Powering off...", end='', flush=True)
        if(self.hv != 0):
            for v in np.linspace(self.hv, 0., 20):
                self.ch_hv.setVoltage(v)
        if(self.bias != 0):
            for v in np.linspace(self.bias, 0., 10):
                self.ch_bias.setVoltage(v)
        time.sleep(0.5)
        self.ch_bdaq.setOn(False)
        time.sleep(0.5)
        self.ch_chip.setOn(False)
        self.ch_bias.setOn(False)
        self.ch_hv.setOn(False)
        
        
        if not before:
            print(" [Done]\ngood night!")

    def rampDown(self):
        if(self.hv != 0):
            for v in np.linspace(self.hv, 0., 20):
                self.ch_hv.setVoltage(v)
        if(self.bias != 0):
            for v in np.linspace(self.bias, 0., 10):
                self.ch_bias.setVoltage(v)

    def rampUp(self):
        if(self.bias != 0):
            for v in np.linspace(0., self.bias, 10):
                self.ch_bias.setVoltage(v)
           
        if(self.hv != 0): 
            for v in np.linspace(0., self.hv, 30):
                self.ch_hv.setVoltage(v)
        
        






