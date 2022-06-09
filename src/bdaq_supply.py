from src.HMP4040 import HMP4040
import time
import os

 



class PowerManager():
    def __init__(self):
        self.ps = HMP4040()
        
        self.ch_bdaq = self.ps.out1   # supply for the bdaq board
        self.ch_chip = self.ps.out4   # supply for the chip (digital)
    
    def __enter__(self):
        self.startup()
        return self
    
    def __exit__(self, a, b, c):
        self.shutdown()
    
    
    
    def startup(self):
        if not self.ps.allOff():
            print("WARNING: not all supplys were switched off!")
            self.shutdown(before=True)
            time.sleep(0.5)
            
        self.ps.reset()
        self.ch_chip.setVoltage(1.8)
        self.ch_chip.setCurrent(0.8)
        self.ch_chip.setFuse(delay=10)
        
        self.ch_bdaq.setVoltage(5.0)
        self.ch_bdaq.setCurrent(1.0)
        self.ch_bdaq.setFuse(delay=50)
        self.ch_chip.linkFuse(self.ch_bdaq.ch)
        

        self.ch_chip.setOn(True)
        time.sleep(0.1)
        self.ch_bdaq.setOn(True)
        time.sleep(0.5)
        print("Power is up, waiting for ping response...", end='', flush=True)
        for i in range(20):
            time.sleep(1.1)
            if os.system("ping -c 1 192.168.10.23 -t 1 > /dev/null") == 0:
                print(" [ OK ]\n Connection to bdaq board ready now!")
                break
    
    
    """ disable all power supply rails in order - may be called with before==True at beginning 
    of script if at least one output was not disabled before (e.g. after a crash) """
    def shutdown(self, before=False):
        if not before:
            print("Powering off...", end='', flush=True)
        time.sleep(0.5)
        self.ch_bdaq.setOn(False)
        time.sleep(0.5)
        self.ch_chip.setOn(False)
        if not before:
            print(" [Done]\ngood night!")









