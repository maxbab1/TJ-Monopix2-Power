import pyvisa as visa
import time
import sys

class K2450smu:
    def __init__(self, port='TCPIP0::169.254.91.1::inst0::INSTR'):
        """Initialize the connection to the instrument"""
        self.rm = visa.ResourceManager()
        # self.inst = self.rm.open_resource(resource_name)
        # print("Connected to:", self.inst.query("*IDN?"))
        try:
            # Try to open the resource
            self.inst = self.rm.open_resource(port)
            # print(f" ")
            # print(f"Connected to: {self.inst.query('*IDN?')}")

        except visa.errors.VisaIOError as e:
            print("ERROR: Could not connect to the instrument.")
            print("Debugging steps:")
            print("   - Is the instrument powered on?")
            print("   - Is the correct resource name being used?")
            print("   - Try running `rm.list_resources()` to check available devices.")
            print("   - Ensure the instrument is connected via USB, LAN, or GPIB.")
            print(f"VISA Error Details: {e}")
            exit(1)

        self.inst.write("SOUR:FUNC VOLT")  # Set source function to voltage
        self.inst.write("SOUR:VOLT:RANG 200")  # Set voltage range
        self.inst.write("SOUR:VOLT:ILIM 0.0003")  # Set current limit to 300 µA
        self.inst.write("SENS:FUNC 'CURR'")  # Set measurement function to current
        self.inst.write("SENS:CURR:RANG 0.001")  # Set current measurement range
        
    def set_voltage(self, voltage):
        """Set the voltage of the SMU"""
        self.inst.write(f"SOUR:VOLT {voltage}")

    def set_current_compl(self, current):
        """Set the voltage of the SMU"""
        self.inst.write(f"SOUR:VOLT:ILIM {current}")

    def get_voltage(self):
        """Return the current set voltage"""
        return float(self.inst.query("SOUR:VOLT?").strip())

    def get_current(self):
        """Measure and return the current value"""
        self.inst.write("*WAI")
        return float(self.inst.query("MEAS:CURR?").strip())

    def close(self):
        """Close the connection to the instrument"""
        self.inst.close()

    def setOn(self, state):
        if state:
            self.inst.write("OUTP ON")
        else:
            self.inst.write("OUTP OFF")
            
    def isOn(self):
        r = self.inst.query("OUTP?").strip()
        return int(r) == 1

            
            
            


