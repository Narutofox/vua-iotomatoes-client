import requests
from apscheduler.schedulers.background import BackgroundScheduler
import json
from json_logic import jsonLogic
from datetime import datetime
import time
from threading import Thread

class ActionManager():
  
    def __init__(self, url_get = None):
        if url_get == None:
            self.url_get = 'http://193.198.208.164:13080/api/farms/1/ruleset'
        else:
            self.url_get = url_get
            
        self.minutes = 15
        self.watering = {1: True, 2: True}
        self.started_date = datetime.now()
        self.sensor_values = []
        self.ruleset = None
        self.__initializeJobs()
            
    def __initializeJobs(self):
        self.__getRuleset()
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.__getRuleset, "interval", seconds=10, id="rest_job")
        self.scheduler.start() 
    
    def __getRuleset(self):
        try: 
            request = requests.get(url=self.url_get)
            request.raise_for_status()
            if request.ok:
                self.ruleset = json.loads(request.content)
        except requests.exceptions.RequestException as e:
            print("Error")
            print(e)
        
    def destroy(self):
        self.scheduler.remove_job(job_id="rest_job")
        
    def get_actions(self, temperature, air_humidity, soil_humidity):
                
        currentDate = datetime.now()
        delta = currentDate - self.started_date
        currentDay = delta.days
        midnight = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds = (currentDate - midnight).seconds
        
        data = { 
            "currentTime" : seconds, 
            "currentDay" : currentDay,
            "soilHumidity": soil_humidity['value'],
            "airTemperature" : temperature,
            "airHumidity" : air_humidity
        }
        
        pump = soil_humidity['pump']
        watering = jsonLogic(json.loads(self.ruleset['wtr']), data) if self.watering[pump] == True else False
        light = jsonLogic(json.loads(self.ruleset['lgt']), data)
        heating = jsonLogic(json.loads(self.ruleset['htn']), data)
        cooling = jsonLogic(json.loads(self.ruleset['cln']), data)

        
        if watering:
            thread = Thread(target = self.__watering_delay, args=[pump])
            thread.start()
        

        actions = {
            'watering': watering,
            'light': light,
            'heating': heating,
            'cooling': cooling
        }
        
        return actions
    
    def __watering_delay(self, pump):
        self.watering[pump] = False
        time.sleep(self.minutes * 60)
        self.watering[pump] = True
    
    def __del__(self):
        self.destroy()