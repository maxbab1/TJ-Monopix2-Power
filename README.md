# TJ-Monopix2-Power
Power supply helper program for Hameg power supplies




# Installation

You need python3 on your system

```git clone git@github.com:maxbab1/TJ-Monopix2-Power.git```
```cd TJ-Monopix2-Power```
```pip install -r requirements.txt```
And for the command alias of ''
```echo "alias bdaq_supply='python `pwd`/standalone_power.py'" >> ~/.bashrc && source ~/.bashrc```


# Usage

usage: bdaq_supply [-h] [-b B] [-p P]

optional arguments:
  -h, --help  show this help message and exit
  -b B        Bias voltage for PSUB/PWELL or HV
  -p P        serial port


