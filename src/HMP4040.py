import serial
import time

class Channel:
    def __init__(self, channel, supply):
        self.supply = supply
        self.ch = channel
    
    def setChannel(self):
        self.supply.command('INST:NSEL {}'.format(self.ch))
    
    
    def setVoltage(self, voltage):
        self.setChannel()
        self.supply.command('VOLT {}V'.format(voltage))
    
    def setCurrent(self, current):
        self.setChannel()
        self.supply.command('CURR {}A'.format(current))
    
    
    def measVoltage(self):
        self.setChannel()
        return float(self.supply.command('MEAS:VOLT?'))
    
    def measCurrent(self):
        self.setChannel()
        return float(self.supply.command('MEAS:CURR?'))
    
    def setFuse(self, to=True, delay=None):
        self.setChannel()
        if to:
            self.supply.command('FUSE on')
        else:
            self.supply.command('FUSE off')
        if delay is not None:  # time to let capacitors charge, in ms
            self.supply.command('FUSE:DELAY {}'.format(delay))
            
    def linkFuse(self, withChannel):
        self.setChannel()
        self.supply.command('FUSE:LINK {}'.format(withChannel))
    
    def setOn(self, state):
        self.setChannel()
        if state:
            self.supply.command('OUTP on')
        else:
            self.supply.command('OUTP off')
            
    def isOn(self):
        self.setChannel()
        r = self.supply.command('OUTP?')
        return int(r) == 1
        
        
    
        
class HMP4040:    
    def __init__(self, port='/dev/ttyUSB1', autoopen=True, debug=False):
        self.serial = serial.Serial(port, 115200, timeout=1)
        self.debug = debug
        self.ch = {}
        self.out1 = Channel(1, self)
        self.out2 = Channel(2, self)
        self.out3 = Channel(3, self)
        self.out4 = Channel(4, self)


        if autoopen:
            self.open()
    
    def open(self):
        if self.serial.is_open:
            self.serial.close()
        self.serial.open()
        self.verify()
        
    def close(self):
        self.serial.close()
    
    def reset(self):
        self.command("*RST")

    def verify(self):
        line = self.command('*IDN?')
        if not line.startswith('HAMEG,HMP4040'):
            raise TypeError('Error: not a HAMEG HMP4040 but '+str(line))
            
    """check if all outputs are currently disabled"""
    def allOff(self):
        return not (self.out1.isOn() or self.out2.isOn() or self.out3.isOn() or self.out4.isOn())
    
    def command(self, cmd):
        if self.debug:
            print("Tx: " + cmd)
        self.serial.write(bytes(cmd+'\n', 'utf-8'))
        time.sleep(0.05)
        if('?' in cmd):
            return self.serial.readline().decode()
        self.checkErrors()
    
    def checkErrors(self):
        if self.serial.in_waiting:
            print("Unhandled message: "+self.serial.readline().decode())
            
            
            
            
            
    







