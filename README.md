# TJ-Monopix2-Power: FEI4 version 
Power supply helper program for Hameg power supplies




# Installation

You need python3 on your system

```git clone git@github.com:maxbab1/TJ-Monopix2-Power.git```
```cd TJ-Monopix2-Power```
```git checkout fei4```
```pip install -r requirements.txt```
And for the command alias of ''
```echo "alias fei4_supply='python `pwd`/standalone_power_fei4.py'" >> ~/.bashrc && source ~/.bashrc```


# Usage

usage: bdaq_supply [-h] [-b B] [-p P]

optional arguments:
  -h, --help  show this help message and exit
  -b B        Bias voltage (3V default)
  -p P        serial port (default: /dev/ttyFEI4)


# Installazion of custom name of serial port:

connect USB and use ```dmesg``` to find the serial number of connected device

sudo vim /dev/udev/rules.d/80-hameg.rules  # and add (with the correct serial number)
    SUBSYSTEMS=="usb", KERNEL=="ttyUSB*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="A8008uJY", SYMLINK+="ttyFEI4"



