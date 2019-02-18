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

allPumps = []
pumpsPins = [
    {'pinBoard':11, 'actuatorId': 1},
    {'pinBoard':13, 'actuatorId': 2},
    {'pinBoard':15, 'actuatorId': 3}
]

allSoil = []
soilPins = [
    {'chPin':7, 'sensorId': 4},
    {'chPin':6, 'sensorId': 5}
]

baseUrl = "http://193.198.208.164:13080/api/"
sensorMeasurmentsUrlSuffix = "sensorMeasurements"

# Pin configuration
lampPin = 36

peltierPin = 40
executePeltierTime = 5 #seconds

motorPin1 = 16
motorPin2 = 18

executeTime = 1 #seconds

for pin in pumpsPins:
    allPumps.append(Classes.Pump(pin['pinBoard']))
    
for ch in soilPins:
    allSoil.append(Classes.Mcp3008(ch['chPin']))

lightSensor = Classes.Mcp3008(5)

def readValues():
    print("1")
    soilHum1 = allSoil[0].read_pct()
    print("2")
    soilHum2 = allSoil[1].read_pct()
    print("3")
    airHum, airTemp = Adafruit_DHT.read_retry(22, 4)
    print("4")
    return [airTemp, airHum, soilHum1, soilHum2]

def sendData(measurements):
    r = requests.post(baseUrl + sensorMeasurmentsUrlSuffix
                      , json={'1': measurements[0],
                              '2': measurements[1],
                              '4': measurements[2],
                              '5': measurements[3]})
    
def light_adc_to_percent(light_adc):
    min = 0
    max = 1023
    return 100 - int(round(((float(light_adc)-min)/(max-min))*100))

manager = ActionManager()

try:
    if __name__ == "__main__":
         while 1:
            print("------ Script start ------")
            
            try:
                measurements = readValues()
                
                lightSensorFromADC = lightSensor.readadc()
                lightSensorValue = light_adc_to_percent(lightSensorFromADC)
                
                actions_plant_1 = manager.get_actions(measurements[0], measurements[1], measurements[2])
                actions_plant_2 = manager.get_actions(measurements[0], measurements[1], measurements[3])
                actions_plant_3 = manager.get_actions(measurements[0], measurements[1], measurements[3])
                
                print("Sending measurements")
                #actuatorCommands = evaluateRules(measurments)
                #startActuators(actuatorCommands)
                #sendData(measurements)
            except:
                #log and ignore to resume
                i=2
            time.sleep(executeTime)
except KeyboardInterrupt:
    print("Exit program")
finally:
    GPIO.cleanup()
