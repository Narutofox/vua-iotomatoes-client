import Classes
import sys
import Adafruit_DHT
import time as time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) #pins number from board

allPumps = []
pumpsPins = [
    {'pinBoard':11, 'sensorId': None},
    {'pinBoard':13, 'sensorId': None},
    {'pinBoard':15, 'sensorId': None}
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
    allPumps.append(Classes.Pump(pin['pinBoard']))
    
for ch in soilPins:
    allSoil.append(Classes.Mcp3008(ch['chPin']))
    
try:
    if __name__ == "__main__":
        
        while 1:
            print("------ Script start ------")
            
            # Configure lamps on/off
            lamp = Classes.Lamp(lampPin)
            lamp.on()
            
            time.sleep(1)
            lamp.off()
            
            time.sleep(1)
            
            # Configure peltier
            peltier = Classes.Peltier(peltierPin)
            peltier.on()
            
            time.sleep(executePeltierTime)
            
            peltier.off()
            time.sleep(1)
            
            # Configure motors
            motor = Classes.Motor(motorPin1, motorPin2)
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
            
            print strSoilAdc
            print strSoil[:-1]
            
            # Read temperature and air humidity
            hum, temp = Adafruit_DHT.read_retry(22, 4)
            print "Temp: %dC, Humidity: %d%%" % (temp, hum)
            
            # Write sensor data to LCD
            LCD = Classes.LCD(29, 31, 33, 35, 37, 38)
            LCD.begin(16,2)
            
            time.sleep(0.5)
            LCD.write("Temp: %dC, Hum: %d%%" % (temp, hum)) 
            LCD.nextline()
            LCD.write(strSoil[:-1])
            
            time.sleep(executeTime)
except KeyboardInterrupt:
    print("Exit program")
finally:
    GPIO.cleanup()
        
	
	