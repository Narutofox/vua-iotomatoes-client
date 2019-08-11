import Classes
import sys
import Adafruit_DHT
import time as time
import RPi.GPIO as GPIO
import json
import requests
from datetime import datetime
from ActionManager import ActionManager

GPIO.setmode(GPIO.BOARD) #pins number from board

WATERING_TIME_SEC = 5
#global MOTOR_RUNTIME
MOTOR_RUNTIME = 5
EXECUTE_PELTIER_TIME = 5 #seconds
EXECUTE_TIME = 60 #seconds

global curr_pos
global counter
curr_pos = "None"
counter = 0



allPumps = []
pumpsPins = [
    {'pinBoard':11, 'actuatorId': 1},
    {'pinBoard':13, 'actuatorId': 2},
    {'pinBoard':15, 'actuatorId': 3}
]

pump1_pin = 11
pump2_pin = 13
pump3_pin = 15

allSoil = []
soilPins = [
    {'chPin':7, 'sensorId': 4},
    {'chPin':6, 'sensorId': 5}
]

baseUrl = "https://cicekthesis.azurewebsites.net/api/"
sensorMeasurmentsUrlSuffix = "sensorMeasurements"

# Pin configuration
lampPin = 36

peltierPin = 40

motorPin1 = 16
motorPin2 = 18

manager = ActionManager()

lamp = Classes.Lamp(lampPin)

pump1 = Classes.Pump(pump1_pin)
pump2 = Classes.Pump(pump2_pin)
pump3 = Classes.Pump(pump3_pin)

peltier = Classes.Peltier(peltierPin)
motor = Classes.Motor(motorPin1, motorPin2)
# Write sensor data to LCD
LCD = Classes.LCD(29, 31, 33, 35, 37, 38)
LCD.begin(16,2)

for pin in pumpsPins:
    allPumps.append(Classes.Pump(pin['pinBoard']))
    
for ch in soilPins:
    allSoil.append(Classes.Mcp3008(ch['chPin']))

lightSensor = Classes.Mcp3008(5)

    
def light_adc_to_percent(light_adc):
    min = 0
    max = 1023
    return 100 - int(round(((float(light_adc)-min)/(max-min))*100))

def readValues():
    soilHum1 = allSoil[0].read_pct()
    soilHum2 = allSoil[1].read_pct()
    airHum, airTemp = Adafruit_DHT.read_retry(22, 4)
    lightSensorFromADC = lightSensor.readadc()
    lightSensorValue = light_adc_to_percent(lightSensorFromADC)
    return [airTemp, airHum, soilHum1, soilHum2, lightSensorValue]

def sendData(measurements):
    r = requests.post(baseUrl + sensorMeasurmentsUrlSuffix
                      , json={'1': measurements[0],
                              '2': measurements[1],
                              '3': measurements[4],
                              '4': measurements[2],
                              '5': measurements[3]})

def evaluateRules(measurments):
    actions_plant_1 = manager.get_actions(measurements[0], measurements[1], {"pump": 1 , "value": measurements[2]})
    actions_plant_2 = manager.get_actions(measurements[0], measurements[1], {"pump": 2 , "value": measurements[3]})
    
    return {
            "pump1": actions_plant_1['watering'],
            "pump2": actions_plant_2['watering'],
            "pump3": actions_plant_2['watering'],
            "heating": actions_plant_1['heating'],
            "cooling": actions_plant_1['cooling'],
            "light": actions_plant_1['light']
        }

def displayOnLCD(measurments):
    global counter
    LCD.clear()
    
    if(counter < 1):
        LCD.write("Temp: %dC, Hum: %d%%" % (measurments[0], measurments[1]))
        LCD.nextline()
        LCD.write("Light: %d%%" % measurments[4])
    else:
        LCD.write("Soil 1: %d%%" % measurments[2])
        LCD.nextline()
        LCD.write("Soil 2: %d%%" % measurments[3])
        
    counter = counter +1
    if(counter == 2):
        counter = 0

def startActuators(actuatorCommands):
    global curr_pos
    #global MOTOR_RUNTIME
    
    if actuatorCommands['light']:
        lamp.on()
    else:
        lamp.off()
        
    
    if (curr_pos != 'htn') & (actuatorCommands['heating']):
        motor.forward()
        time.sleep(MOTOR_RUNTIME)
        motor.stop()
        curr_pos = 'htn'
        
    
    if (curr_pos != 'cln') & (actuatorCommands['cooling']):
        motor.reverse()        
        time.sleep(MOTOR_RUNTIME)
        motor.stop()
        curr_pos = 'cln'
        
    if ((actuatorCommands['heating']) | (actuatorCommands['cooling'])):
        peltier.on()
    else:
        peltier.off()
        
        
    if actuatorCommands['pump1']:
        pump1.runPump(WATERING_TIME_SEC)
        
        
    if actuatorCommands['pump2']:
        pump2.runPump(WATERING_TIME_SEC)
        
        
    if actuatorCommands['pump3']:
        pump3.runPump(WATERING_TIME_SEC)
        

try:
    if __name__ == "__main__":
         while 1:
            print("------ Script start ------")
            
            try:            
                print('Reading values')
                measurements = readValues()
                print('Displaying values')
                displayOnLCD(measurements)                
                print('Evaluating rules')
                actuatorCommands = evaluateRules(measurements)
                print('Starting commands')
                startActuators(actuatorCommands)
                print("Sending measurements")
                print(measurements)
                sendData(measurements)
            except:
                print("Error")
            time.sleep(EXECUTE_TIME)
except KeyboardInterrupt:
    print("Exit program")
finally:
    GPIO.cleanup()
