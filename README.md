# TJ-Monopix2-Power
Power supply helper program for Hameg power supplies
On a freshly powered on Supply, the first attempt sometimes fails, try to execute the script a second time in that case (known bug)

# Usage

Connections of the power supply:
* CH1: BDAQ53 Board (5V)
* CH2: TJ-Monopix2 PSUB/PWELL
* CH3: TJ-Monopix2 HV
* CH4: TJ-Monopix2 LV (1.8V)

If you want to bias the chip with PSUB/PWELL, you need to specify the ```--bias``` parameter. When there is nothing more specified, it defaults to 3V, or you can use eg ```--bias 5``` for 5 volts.

If you want to bias the chip with HV, you need to specify the ```--hv``` parameter. When there is nothing more specified, it defaults to 5V, or you can use eg ```--hv 10``` for 10 volts.

Both options from above are mutally exclusive, except you use the ```--f``` flag.

You can specify a custom seial port via ```-p /dev/ttyUSB0```



# Installation

You need python3 on your system

```git clone git@github.com:maxbab1/TJ-Monopix2-Power.git```

```cd TJ-Monopix2-Power```

```pip install -r requirements.txt```

And for the command alias of ''

```echo "alias bdaq_supply='python `pwd`/standalone_power.py'" >> ~/.bashrc && source ~/.bashrc```

# Installation of custom name of serial port:

connect USB and use ```dmesg | grep usb``` to find the serial number of connected device

```sudo vim /etc/udev/rules.d/80-hameg.rules```  # and add (with the correct serial number)

    SUBSYSTEMS=="usb", KERNEL=="ttyUSB*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="ed72", ATTRS{serial}=="A8008uJY", SYMLINK+="ttyMP2"


# Help

usage: standalone_power.py [-h] [--bias [BIAS [BIAS ...]]] [--hv [HV [HV ...]]] [-f] [-p P]

optional arguments:
  -h, --help            show this help message and exit
  --bias [BIAS [BIAS ...]]
                        Bias voltage for PSUB/PWELL on CH2 of PS
  --hv [HV [HV ...]]    Bias voltage for HV on CH3 of PS
  -f                    accept nonzero Bias and HV at the same time
  -p P                  serial port



