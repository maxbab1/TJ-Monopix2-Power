# TJ-Monopix2-Power
Power supply helper program for Hameg power supplies




# Installation

You need python3 on your system

```git clone git@github.com:maxbab1/TJ-Monopix2-Power.git```

```cd TJ-Monopix2-Power```

```pip install -r requirements.txt```

And for the command alias of ''

```echo "alias bdaq_supply='python `pwd`/standalone_power.py'" >> ~/.bashrc && source ~/.bashrc```

# Installation of custom name of serial port:

connect USB and use ```dmesg | grep usb``` to find the serial number of connected device

```sudo vim /dev/udev/rules.d/80-hameg.rules```  # and add (with the correct serial number)

    SUBSYSTEMS=="usb", KERNEL=="ttyUSB*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="ed72", ATTRS{serial}=="A8008uJY", SYMLINK+="ttyMP2"


# Usage

usage: bdaq_supply [-h] [-b B] [-p P]

optional arguments:
  -h, --help  show this help message and exit
  -b B        Bias voltage for PSUB/PWELL or HV
  -p P        serial port


