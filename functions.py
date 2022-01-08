import logging
from os import system, name, _exit
from di2008.instrument import Di2008
from csv_logger import CsvLogger

#Clear Screen Function
def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

#Print Thermocouple Values
def printVals(ports, sensorType):
    if(sensorType == 'thermocouple'):
        unit = '°C'
    elif(sensorType == 'flux'):
        unit = 'W/m^2'
    else:
        print('Unrecognized sensor type')
        return -1
    
    for channel, port in enumerate(ports, start=1):
        print(f'{sensorType} CH{channel} value: {port.value:.02f} {unit}')
        print() 

#Bang Bang controller. Compares thermocouple readings to desired temperature and modifies peltier state to maintain within deadband.
def bangBang(desiredTemp, deadband, thermocouplePorts, LOGIC_PINS, daq = Di2008):
    #Peltier states
    stateNames = ["Cooling", "Deadband", "Heating"]

    #Temperature calculations
    maxTemp = desiredTemp + deadband
    minTemp = desiredTemp - deadband    
    
    for port in thermocouplePorts:
        #Cooling
        if(port.value > maxTemp):
            state = stateNames[0]

        #Heating
        elif(port.value < minTemp):
            state = stateNames[2]
        
        #Deadband
        else:
            state = stateNames[1]

        #Provide appropriate logic to H-Bridge to modify peltier state
        for pinGroup in LOGIC_PINS:
            #Cooling
            if(state == 0):
                daq.write_do(pinGroup[0], True)
                daq.write_do(pinGroup[1], False)
            
            #Heating
            if(state == 2):
                daq.write_do(pinGroup[0], False)
                daq.write_do(pinGroup[1], True)
            
            #Deadband
            if(state == 1):
                daq.write_do(pinGroup[0], False)
                daq.write_do(pinGroup[1], False)

def log(relativeTime, thermocouplePorts, fluxPorts, peltierState):
    filename = 'data.csv'
    level = logging.INFO
    fmt = '%(message)s'
    datefmt = '%Y/%m/%d %H:%M:%S'
    header = ['relativeTime', 'Thermocouple 1 Value', 'Thermocouple 2 Value', 'Thermocouple 3 Value'] 
    header += ['Heat Flux 1 Value', 'Heat Flux 2 Value', 'Heat Flux 3 Value']
    header += ['Peltier 1 State', 'Peltier 2 State', 'Peltier 3 State']

    # Creat logger with csv rotating handler
    csvlogger = CsvLogger(filename=filename,
                      level=level,
                      fmt=fmt,
                      header=header)
    thermocoupleData = [pin.value for pin in thermocouplePorts]
    fluxData = [pin.value for pin in thermocouplePorts]
    data = [relativeTime]
    data += thermocoupleData
    data += fluxData
    

