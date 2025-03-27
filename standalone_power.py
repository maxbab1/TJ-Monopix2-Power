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

import argparse
import signal
import time
from datetime import datetime

from src.bdaq_supply import PowerManager
from src.monitor import Monitor

parser = argparse.ArgumentParser()
parser.add_argument('--psub', action='store', nargs='*', help='Bias voltage for PSUB (absolute value)')
parser.add_argument('--hv', action='store', nargs='*', help='Bias voltage for HV')
parser.add_argument('-f', action='store_true', default=None, help='accept nonzero Bias and HV at the same time')
parser.add_argument('-p', default='/dev/ttyMP2', help='serial port')
args = parser.parse_args()





# =========   begin handle ctrl-C    =========
def exit_handler(signum, frame):
    print("")
    exit(0)

signal.signal(signal.SIGINT, exit_handler)
# =========   end handle ctrl-C    =========

if args.psub is None:
    psub = 0
elif len(args.psub) == 0:
    psub = 0.0
else:
    psub = float(args.psub[0])

if args.hv is None:
    hv = 0
elif len(args.hv) == 0:
    hv = 5.0
else:
    hv = float(args.hv[0])


if hv == 0 and psub == 0:
    print("WARNING: no bias nor HV selected")

elif hv != 0 and psub != 0:
    if args.f:
        print("WARNING: psub and HV used at the same time")
    else:
        print("ERROR: bias and HV used at the same time (use -f to ignore this)")
        exit(1)

if psub < 6.0 and hv == 0.0:
    print("ERROR: PSUB < 6V")
    exit(1)

if psub > 20.0:
    print("ERROR: PSUB > 20V")
    exit(1)

if hv > 45.0:
    print("ERROR: HV > 45V")
    exit(1)

pwell = 0.0
if psub != 0:
    print("PSUB voltage {:2.1f}V".format(psub))
    pwell = 6.0
    print("PWELL voltage {:2.1f}V".format(pwell))

if hv != 0:
    print("HV voltage   {:2.1f}V".format(hv))

UP = "\x1B[1A"
CLR = "\x1B[0K"


class CHWrapper:
    def __init__(self, name, channel):
        self.ch = channel
        self.name = name
        self.measure()
        
    def measure(self):
        self.u = self.ch.measVoltage()
        self.i = self.ch.measCurrent()
        
    def print(self):
        print(self.name+":")
        print("      {:4.2f} V".format(self.u))
        print("    {:5.1f} mA".format(self.i*1e3))
        print("")


with PowerManager(serial=args.p, psub=psub, pwell=pwell, hv=hv) as pm:
    # -------    begin the testing-payload    -------
    print("ctrl-C to poweroff again and exit")
    chs = []
    # chs.append(CHWrapper("CH1: BDAQ53 Board", pm.ch_bdaq))
    # chs.append(CHWrapper("CH2: PSUB/PWELL", pm.ch_bias))
    # chs.append(CHWrapper("CH3: HV", pm.ch_hv))
    # chs.append(CHWrapper("CH4: LV supply", pm.ch_chip))
    
    while True:
        currtime = datetime.now().strftime("%H:%M:%S")
        print(" "*30, currtime)
        for l in chs:
            l.print()
        time.sleep(0.1)
        for l in chs:
            l.measure()


        print(UP*(len(chs)*4+2))
    # -------      end testing-payload        -------














