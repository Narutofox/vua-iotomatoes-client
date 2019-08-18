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

GPIO.setmode(GPIO.BOARD) #pins number from board

allPumps = []
pumpsPins = [
    {'pinBoard':11, 'sensorId': None}, # p1
    {'pinBoard':13, 'sensorId': None}, # p2
    {'pinBoard':15, 'sensorId': None}  # p3
]

allSoil = []
soilPins = [
    {'chPin':7, 'sensorId': None},
    {'chPin':6, 'sensorId': None}
]

# Pin configuration
lampPin = 36

peltierPin = 40
executePeltierTime = 5 #seconds

motorPin1 = 16
motorPin2 = 18

executeTime = 5 #seconds

for pin in pumpsPins:
    allPumps.append(Pump(pin['pinBoard']))
    
for ch in soilPins:
    allSoil.append(Mcp3008(ch['chPin']))
    
try:
    if __name__ == "__main__":
        
        while 1:
            print("------ Script start ------")
            
            # Configure lamps on/off
            lamp = Lamp(lampPin)
            lamp.on()
            
            time.sleep(1)
            lamp.off()
            
            time.sleep(1)
            
            # Configure peltier
            peltier = Peltier(peltierPin)
            peltier.on()
            
            time.sleep(executePeltierTime)
            
            peltier.off()
            time.sleep(1)
            
            # Configure motors
            motor = Motor(motorPin1, motorPin2)
            motor.forward()
            
            time.sleep(3)
            
            motor.stop()
            time.sleep(1)
            motor.reverse()
            time.sleep(3)
            motor.stop()
            
            # Run pumps
            print("Pumps starting:")
            for pump in allPumps:
                pump.runPump(2)
            
            # Read soil humidity
            strSoil = 'Soil: '
            strSoilAdc = 'Soil adc: '
            
            for soil in allSoil:
                strSoil += str(soil.read_pct()) + '%, '
                strSoilAdc += str(soil.readadc()) + ', '
            
            print(strSoilAdc)
            print(strSoil[:-1])
            
            # Read temperature and air humidity
            hum, temp = Adafruit_DHT.read_retry(22, 4)
            print("Temp: %dC, Humidity: %d%%" % (temp, hum))
            
            # Write sensor data to LCD
            LCDisplay = LCD(29, 31, 33, 35, 37, 38)
            LCDisplay.begin(16,2)
            
            time.sleep(0.5)
            LCDisplay.write("Temp: %dC, Hum: %d%%" % (temp, hum)) 
            LCDisplay.nextline()
            LCDisplay.write(strSoil[:-1])
            
            time.sleep(executeTime)
except KeyboardInterrupt:
    print("Exit program")
finally:
    GPIO.cleanup()