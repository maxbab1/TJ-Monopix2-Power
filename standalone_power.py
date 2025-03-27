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
import os, datetime
from datetime import datetime

from src.bdaq_supply import PowerManager
from src.monitor import Monitor

parser = argparse.ArgumentParser()
parser.add_argument('--psub', action='store', nargs='*', help='Bias voltage for PSUB (absolute value)')
parser.add_argument('--hv', action='store', nargs='*', help='Bias voltage for HV')
parser.add_argument('-f', action='store_true', default=None, help='accept nonzero Bias and HV at the same time')
parser.add_argument('-p', default='/dev/ttyMP2', help='serial port')
args = parser.parse_args()

LOGDIR = 'logs/'
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)
log_file = f"{LOGDIR}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_power_log.csv"

def append_log(ch_bdaq, ch_pwell, ch_psubwell, ch_chip, smu):
    file_exists = os.path.isfile(log_file)
    with open(log_file, 'a', newline='') as f:
        if not file_exists:
            f.write(f'Time, U_FPGA/V, I_FPGA/mA, U_PWELL/V, I_PWELL/mA, U_PSUB/V, I_PSUBWELL/mA, U_LV/V, I_LV/mA, U_HV/V, I/HV/uA')
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"{ts}, " \
               f"{ch_bdaq.measVoltage():.3f}, {ch_bdaq.measCurrent()*1e3:3.1f}, " \
               f"{ch_pwell.measVoltage():.3f}, {ch_pwell.measCurrent()*1e3:3.1f}, " \
               f"{ch_psubwell.measVoltage():2.3f}, {ch_psubwell.measCurrent()*1e3:3.1f}, " \
               f"{ch_chip.measVoltage():2.3f}, {ch_chip.measCurrent()*1e3:3.1f}, " \
               f"{smu.get_voltage():2.3f}, {smu.get_current()*1e6:3.1f}"
        f.write(f"{line}/n")

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

    while True:
        append_log(pm.ch_bdaq, pm.ch_pwell, pm.ch_psubwell, pm.ch_chip, pm.smu)
        time.sleep(1)

    # -------      end testing-payload        -------














