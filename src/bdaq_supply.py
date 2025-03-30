from src.HMP4040 import HMP4040
from src.K2450smu import K2450smu
import time
import os
import numpy as np
 



class PowerManager():
    def __init__(self, serial, psub, pwell, hv):
        self.ps = HMP4040(port=serial)
        self.psub = psub
        self.pwell = pwell
        self.psubwell = psub - pwell
        self.hv = hv
        
        self.ch_bdaq = self.ps.out1   # supply for the bdaq board
        self.ch_chip = self.ps.out4   # supply for the chip (digital)
        
        self.ch_pwell      = self.ps.out2   # supply for the Bias supply
        self.ch_psubwell   = self.ps.out3   # supply for the HV supply

        self.smu = K2450smu()
    
    def __enter__(self):
        self.startup()
        return self
    
    def __exit__(self, a, b, c):
        self.shutdown()
    
    
    def init(self):
        if not self.ps.allOff() or self.smu.isOn():
            if self.ch_psubwell.isOn():
                vstart = self.ch_psubwell.measVoltage()
                for v in np.arange(vstart, 0., -0.5):
                    self.ch_psubwell.setVoltage(v)
                    time.sleep(0.1)
                self.ch_psubwell.setVoltage(0)
            if self.ch_pwell.isOn():
                vstart = self.ch_pwell.measVoltage()
                for v in np.arange(vstart, 0., -0.5):
                    self.ch_pwell.setVoltage(v)
                    time.sleep(0.1)
                self.ch_pwell.setVoltage(0)
            if self.smu.isOn():
                vstart = self.smu.get_voltage()
                for v in np.arange(vstart, 0., -0.5):
                    self.smu.set_voltage(v)
                    time.sleep(0.1)
                self.smu.set_voltage(0)
            
            self.shutdown(before=True)
            time.sleep(0.5)

        self.ps.reset()
        self.ch_chip.setVoltage(1.8)
        self.ch_chip.setCurrent(1.0)
        self.ch_chip.setFuse(delay=50)
        
        self.ch_bdaq.setVoltage(5.0)
        self.ch_bdaq.setCurrent(2.0)
        self.ch_bdaq.setFuse(delay=50)
        self.ch_chip.linkFuse(self.ch_bdaq.ch)
        
        self.ch_pwell.setVoltage(0.0)
        self.ch_pwell.setCurrent(0.005)
        self.ch_pwell.setFuse(delay=50)
        self.ch_pwell.linkFuse(self.ch_bdaq.ch)
        self.ch_pwell.linkFuse(self.ch_chip.ch)
        self.ch_chip.linkFuse(self.ch_psubwell.ch)
        
        self.ch_psubwell.setVoltage(0.0)
        self.ch_psubwell.setCurrent(0.005)
        self.ch_psubwell.setFuse(delay=50)
        self.ch_psubwell.linkFuse(self.ch_bdaq.ch)
        self.ch_psubwell.linkFuse(self.ch_chip.ch)
        self.ch_chip.linkFuse(self.ch_pwell.ch)

        self.smu.set_voltage(0.0)
        self.smu.set_current_compl(0.0003)
        
        self.ch_pwell.setOn(True)
        self.ch_psubwell.setOn(True)
        self.smu.setOn(True)
        time.sleep(0.1)
        self.ch_chip.setOn(True)
        time.sleep(0.1)
        self.ch_bdaq.setOn(True)

    
    def configure(self):
        if self.ps.allOff():
            self.init()
        self.rampUp()
        print("Power is up!")

    def startup(self):
        self.init()
        self.configure()
    

    
    """ disable all power supply rails in order - may be called with before==True at beginning 
    of script if at least one output was not disabled before (e.g. after a crash) """
    def shutdown(self, before=False):
        if not before:
            print("Powering off...", end='', flush=True)
            self.rampDown()
        time.sleep(0.5)
        self.ch_bdaq.setOn(False)
        time.sleep(0.5)
        self.ch_chip.setOn(False)
        self.ch_psubwell.setOn(False)
        self.ch_pwell.setOn(False)
        self.smu.setOn(False)
        
        if not before:
            print(" [Done]\ngood night!")

    def rampDown(self):
        if(self.psubwell != 0):
            for v in np.arange(self.psubwell, 0., -0.5):
                self.ch_psubwell.setVoltage(v)
                time.sleep(0.1)
            self.ch_psubwell.setVoltage(0)
        if(self.pwell != 0):
            for v in np.arange(self.pwell, 0., -0.5):
                self.ch_pwell.setVoltage(v)
                time.sleep(0.1)
            self.ch_pwell.setVoltage(0)
        if(self.hv != 0):
            for v in np.arange(self.hv, 0, -0.5):
                self.smu.set_voltage(v)
                time.sleep(0.5)
            self.smu.set_voltage(0)
        

    def rampUp(self):
        if(self.pwell != 0):
            for v in np.arange(0., self.pwell, 0.5):
                self.ch_pwell.setVoltage(v)
                time.sleep(0.1)
            self.ch_pwell.setVoltage(self.pwell)
        if(self.psubwell != 0):
            for v in np.arange(0., self.psubwell, 0.5):
                self.ch_psubwell.setVoltage(v)
                time.sleep(0.1)
            self.ch_psubwell.setVoltage(self.psubwell)
        if(self.hv != 0):
            for v in np.arange(0., self.hv, 0.5):
                self.smu.set_voltage(v)
                time.sleep(0.5)
            self.smu.set_voltage(self.hv)
        
        
        






