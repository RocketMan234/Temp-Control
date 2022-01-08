import logging
from time import sleep
from di2008 import Di2008, DigitalDirection, AnalogPort, RatePort
from os import system, name, _exit
from csv_logger import CsvLogger
from functions import clear, printVals, bangBang
import signal
import sys


#logging.basicConfig(level=logging.DEBUG)

#Number of controllers used in system
numControllers = 3

#Temperature Settings
desiredTemp = 20
deadband = 2.0

#How long to run the system for, in seconds
maxTime = 600

#How many times to check and modify the peltier state per second
refreshRate = 1
refreshPeriod = 1/refreshRate

#How many times to log data per second
loggingRate = 5
loggingPeriod = 1/loggingRate

#Do not modify
count = 0

"""
Initialize pins. 
Each peltier is initialized with two digital logic outputs stored as lists of ascending integers. [1, 2], [3, 4], ..., [2n + 1, 2n +2]. 
Thermocouples are initialized with one analog pin 1, 2, ..., n. 
Flux sensors are initalized with one analog pin numControllers, numControllers + 1, ..., numControllers + n. (4, 5, 6 for numControllers = 3)
"""
LOGIC_PINS = [list(range(2*i + 1, 2*i + 3)) for i in range(numControllers)]
THERMOCOUPLE_PINS = [i + 1 for i in range(numControllers)]
FLUX_PINS = [i + numControllers + 1 for i in range(numControllers)]
ANALOG_PINS = THERMOCOUPLE_PINS + FLUX_PINS

#Initialize thermocouple and flux sensor ports as analog inputs
thermocouplePorts = [AnalogPort(pin, thermocouple_type= 't') for pin in THERMOCOUPLE_PINS]
fluxPorts = [AnalogPort(pin) for pin in THERMOCOUPLE_PINS]
analogPorts = thermocouplePorts + fluxPorts

#Initialize DAQ and scan analog ports for data
daq = Di2008()
daq.create_scan_list(
    analogPorts
)


daq.start()
for controller in LOGIC_PINS:
    for pin in controller:
        daq.setup_dio_direction(pin, DigitalDirection.OUTPUT)
        print(f"Setting pin {pin} as digital output")

#Check that all analog sensors are returning values before logging
analogVals = [pin.value for pin in ANALOG_PINS]
while not all(analogVals):
    sleep(0.1)
    analogVals = [pin.value for pin in ANALOG_PINS]

sleep(2)

'''
This entire loop checks the temperature value and changes the peltier state accordingly. 
It's enclosed in a try-except block so that a KeyboardInterrupt will stop both the DAQ and the script
'''
try:
    while count < maxTime:

        #Print thermocouple & heat flux values
        printVals(thermocouplePorts)
        printVals(fluxPorts)

        #Temperature Control    
        
        if(count % refreshPeriod) == 0:
            bangBang(desiredTemp, deadband, thermocouplePorts, LOGIC_PINS, daq)
        
        
        count += refreshPeriod
        sleep(refreshPeriod) 
        
        clear()

except KeyboardInterrupt:
    print("Keyboard Interrupt Detected. Shutting down...")
    daq.close()
    sys.exit(0)
