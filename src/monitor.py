import subprocess
import time
from collections import deque
from datetime import datetime


class Monitor:
    def __init__(self, enable, history=200):
        self.gp = None
        if enable:
            self.gp = subprocess.Popen(["gnuplot", '-p'], shell=True, stdin=subprocess.PIPE)

        self.time = deque(maxlen=history)
        self.i_bdaq = deque(maxlen=history)
        self.i_bias = deque(maxlen=history)
        self.i_hv = deque(maxlen=history)
        self.i_lv = deque(maxlen=history)
        self.history = history

    def init(self):
        if not self.gp:
            return
        self.gp.stdin.write(b'set grid\n')
        self.gp.stdin.write(b'set ylabel "I / mA"\n')
        self.gp.stdin.write(b'set lmargin at screen 0.1; set rmargin at screen 0.98\n')
        self.gp.stdin.write(f'set xrange [-{self.history}:0]\n'.encode())

        # self.gp.stdin.write(b'set xdata time\n')
        # self.gp.stdin.write(b'set timefmt "%H:%M:%S"\n')

        self.gp.stdin.flush()

    def add_values(self, i_bdaq, i_bias, i_hv, i_lv):
        if not self.gp:
            return
        self.i_bdaq.append(i_bdaq*1e3)
        self.i_bias.append(i_bias*1e3)
        self.i_hv.append(i_hv*1e3)
        self.i_lv.append(i_lv*1e3)
        self.time.append(datetime.now())

    def plot(self):
        if not self.gp:
            return

        now = datetime.now()
        self.gp.stdin.write(b'set multiplot layout 4, 1\n')
        self.gp.stdin.write(f'unset xlabel \n'.encode())
        self.gp.stdin.write(f'set format x "" \n'.encode())

        self.gp.stdin.write(b'set tmargin at screen 0.98; set bmargin at screen 0.68\n')
        self.gp.stdin.write(b'plot "-" using 1:2 w l title "BDAQ"\n')
        for t, v in zip(self.time, self.i_bdaq):
            self.gp.stdin.write(f'{(t-now).total_seconds()} {v}\n'.encode())
        self.gp.stdin.write(b"e\n")

        self.gp.stdin.write(b'set tmargin at screen 0.65; set bmargin at screen 0.55\n')
        self.gp.stdin.write(b'plot "-" using 1:2 w l title "PSUB/PWELL"\n')
        for t, v in zip(self.time, self.i_bias):
            self.gp.stdin.write(f'{(t - now).total_seconds()} {v}\n'.encode())
        self.gp.stdin.write(b"e\n")

        self.gp.stdin.write(b'set tmargin at screen 0.53; set bmargin at screen 0.43\n')
        self.gp.stdin.write(b'plot "-" using 1:2 w l title "HV"\n')
        for t, v in zip(self.time, self.i_hv):
            self.gp.stdin.write(f'{(t - now).total_seconds()} {v}\n'.encode())
        self.gp.stdin.write(b"e\n")

        self.gp.stdin.write(b'set tmargin at screen 0.41; set bmargin at screen 0.11\n')
        self.gp.stdin.write(f'set xlabel "time / seconds"\n'.encode())
        self.gp.stdin.write(f'unset format x\n'.encode())
        self.gp.stdin.write(b'plot "-" using 1:2 w l title "LV"\n')
        for t, v in zip(self.time, self.i_lv):
            self.gp.stdin.write(f'{(t - now).total_seconds()} {v}\n'.encode())
        self.gp.stdin.write(b"e\n")



        self.gp.stdin.flush()


