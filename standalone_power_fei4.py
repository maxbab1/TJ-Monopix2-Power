# ------------------------------------------------------------
# TJ-Monopix2: controlled and reproducible power-up sequence using the HMP4040 power supply
# 
# The script is on one hand intended to be run side-by-side other testing-scripts
# as well as a template for scripts that include the power management
#
# The script will tell you when 
# 
# ------------------------------------------------------------
#
import os
import yaml

from src.bdaq_supply import PowerManager
import time
import signal
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-b', default=3.0, help='Bias voltage')
parser.add_argument('-p', default='/dev/ttyFEI4', help='serial port')
args = parser.parse_args()





# =========   begin handle ctrl-C    =========
def exit_handler(signum, frame):
    print("")
    exit(0)

signal.signal(signal.SIGINT, exit_handler)
# =========   end handle ctrl-C    =========


bias = float(args.b)
print("Bias voltage {:2.1f}".format(bias))

with PowerManager(serial=args.p, bias=bias) as pm:
    # -------    begin the testing-payload    -------
    print("ctrl-C to poweroff again and exit")
    print("Waiting for first chip configuration before ramping up HV")
    hv_up = False
    while True:
        time.sleep(1)
        currtime = datetime.now().strftime("%H:%M:%S")
        vbdaq = pm.ch_bdaq.measVoltage()
        ibdaq = pm.ch_bdaq.measCurrent()
        vchip = pm.ch_chip.measVoltage()
        ichip = pm.ch_chip.measCurrent()
        print("{}  Chip LV: {:4.2f}V  {:5.1f}mA,  BDAQ: {:3.1f}V  {:5.1f}mA".format(currtime, vchip, ichip*1e3, vbdaq, ibdaq*1e3))
        
        if not hv_up and ichip > 0.002:
            hv_up = True
            time.sleep(2)
            print("Ramping up HV")
            pm.ramp_up_hv()
        
        
    # -------      end testing-payload        -------



exit(0)












