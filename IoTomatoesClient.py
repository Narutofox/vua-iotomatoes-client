from Classes.Pump import Pump
from Classes.LiquidCrystalPi import LCD
from Classes.Lamp import Lamp
from Classes.Mcp3008 import Mcp3008
from Classes.Peltier import Peltier
from Classes.Motor import Motor
import sys
import Adafruit_DHT
import time as time
import RPi.GPIO as GPIO
import json
import requests
from datetime import datetime
from ActionManager import ActionManager
from Classes.WebServer import MyServer
from http.server import BaseHTTPRequestHandler, HTTPServer

GPIO.setmode(GPIO.BOARD) #pins number from board

WATERING_TIME_SEC = 5
#global MOTOR_RUNTIME
MOTOR_RUNTIME = 5
EXECUTE_PELTIER_TIME = 5 #seconds
EXECUTE_TIME = 60 #seconds
 
global curr_pos
global counter
lastAirTemp, lastAirHum, lastSoilHum1, lastLight = 0,0,0,0
curr_pos = "None"
counter = 0
airTempSensorId, airHumSensorId, soilHum1SensorId, lightSensorId = 0,0,0,0


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
farmId = 1;
baseUrl = "https://cicekthesis.azurewebsites.net/api/"
sensorMeasurmentsUrlSuffix = "sensorMeasurements"

# Pin configuration
lampPin = 36

peltierPin = 40

motorPin1 = 16
motorPin2 = 18

manager = ActionManager()

lamp = Lamp(lampPin)

pump1 = Pump(pump1_pin)
pump2 = Pump(pump2_pin)
pump3 = Pump(pump3_pin)

peltier = Peltier(peltierPin)
motor = Motor(motorPin1, motorPin2)
myServer = MyServer(manager)
# Write sensor data to LCD
LCDisplay = LCD(29, 31, 33, 35, 37, 38)
LCDisplay.begin(16,2)

for pin in pumpsPins:
    allPumps.append(Pump(pin['pinBoard']))
    
for ch in soilPins:
    allSoil.append(Mcp3008(ch['chPin']))

lightSensor = Mcp3008(5)

airHumAirTempPin = 4
airHumAirTempSensor = Adafruit_DHT.DHT22
currentActuatorCommands = {
			'watering': False,
			'light': False,
			'heating': False,
			'cooling': False
		}

def light_adc_to_percent(light_adc):
    min = 0
    max = 1023
    return 100 - int(round(((float(light_adc)-min)/(max-min))*100))

def readValues():
    soilHum1 = allSoil[0].read_pct()
    airHum, airTemp = Adafruit_DHT.read_retry(airHumAirTempSensor, airHumAirTempPin)
    lightSensorFromADC = lightSensor.readadc()
    lightSensorValue = light_adc_to_percent(lightSensorFromADC)
    return [airTemp, airHum, soilHum1, lightSensorValue]

def sendData(measurements):
	airTemp = measurements[0]
	airHum = measurements[1]
	soilHum = measurements[2]
	lightSensor = measurements[3]
	
	if 	(int(airTemp) != lastAirTemp) or (int(airHum) != lastAirHum) or (int(soilHum) != lastSoilHum1) or (int(lightSensor) != lastLight):

		r = requests.post(baseUrl + sensorMeasurmentsUrlSuffix
						  , json={'FarmId': farmId,
								  'Temperature': airTemp,
								  'AirHumidity': airHum,
								  'SoilHumidity': soilHum,
								  'Light': lightSensor})
	
	lastAirTemp, lastAirHum, lastSoilHum1, lastLight = int(float(airTemp)),int(float(airHum)), int(float(soilHum)),int(float(lightSensor))

def evaluateRules(measurments):
    actions_plant_1 = manager.get_actions(measurements[0], measurements[1], {"pump": 1 , "value": measurements[2]},currentActuatorCommands)
    
    return {
            "pump1": actions_plant_1['watering'],
            "heating": actions_plant_1['heating'],
            "cooling": actions_plant_1['cooling'],
            "light": actions_plant_1['light']
        }

def displayOnLCD(measurments):
    global counter
    LCDisplay.clear()
    
    if(counter < 1):
        LCDisplay.write("Temp: %dC, Hum: %d%%" % (measurments[0], measurments[1]))
        LCDisplay.nextline()
        LCDisplay.write("Light: %d%%" % measurments[4])
    else:
        LCDisplay.write("Soil 1: %d%%" % measurments[2])
        LCDisplay.nextline()
        LCDisplay.write("Soil 2: %d%%" % measurments[3])
        
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
 
def get_ip_address():
	url = "https://api.ipify.org/?format=json" # Napraviti novi kontroler na web api koj vraća IP addresu sa koje je zahtjev poslan
	request = requests.get(url)
	if request.ok:
		content = json.loads(request.content)
		return content["ip"]
	return "";
	
try:
	if __name__ == "__main__":	
		hostName = get_ip_address()  # Change this to your Raspberry Pi IP address
		hostPort = 8000
		httpServer = HTTPServer((hostName, hostPort), myServer)
		print("Server Starts - %s:%s" % (hostName, hostPort))
		httpServer.serve_forever()		
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
				currentActuatorCommands = actuatorCommands;
				startActuators(actuatorCommands)
				print("Sending measurements")
				print(measurements)
				sendData(measurements)
			except:
				print("Error")
			time.sleep(EXECUTE_TIME)
except KeyboardInterrupt:
	http_server.server_close()
	print("Exit program")
finally:
    GPIO.cleanup()
