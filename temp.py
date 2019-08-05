#!/usr/bin/python
import sys
import Adafruit_DHT
import requests
import time
import json

while True:
    sensor = Adafruit_DHT.DHT22
    pin = 4 
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    print('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity))
    time.sleep(1)
    url = 'http://e6c6915f.ngrok.io/api/sensors'
    data = {"humidity": humidity, "temperature": temperature}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.status_code)
