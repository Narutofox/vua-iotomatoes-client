import requests
from apscheduler.schedulers.background import BackgroundScheduler
import json
from json_logic import jsonLogic
from datetime import datetime

class ActionManager():
  
    def __init__(self, url_get = None):
        if url_get == None:
            self.url_get = 'http://193.198.208.164:13080/api/farms/1/ruleset'
        else:
            self.url_get = url_get
        
        self.started_date = datetime.now()
        self.sensor_values = []
        self.url_post = 'http://localhost:50441/api/farms/'
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
        
        #self.__save_metrics(temperature, air_humidity, soil_humidity)
                
        currentDate = datetime.now()
        delta = currentDate - self.started_date
        currentDay = delta.days
        
        midnight = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds = (currentDate - midnight).seconds
        
        data = { 
            "currentTime" : seconds, 
            "currentDay" : currentDay,
            "soilHumidity": soil_humidity['value'],
            "temperature" : temperature['value'],
            "airHumidity" : air_humidity['value']
        }
        
        water = jsonLogic(json.loads(self.ruleset['wtr']), data) if soil_humidity != None else None
        light = jsonLogic(json.loads(self.ruleset['lgt']), data)
        heating = jsonLogic(json.loads(self.ruleset['htg']), data)
        cooling = jsonLogic(json.loads(self.ruleset['clg']), data)
        
        actions = {
            'water': water,
            'light': light,
            'heating': heating,
            'cooling': cooling
        }
        
        return actions
    
    def __save_metrics(self, temperature, air_humidity, soil_humidity):
                
        metrics_json = { 
            "Temperature" : temperature, 
            "AirHumidity" : air_humidity,
            "SoilHumidity": soil_humidity
        }
        
        try: 
            request = requests.post(url=self.url_post, data = metrics_json)
            request.raise_for_status()
            
            if len(self.sensor_values) > 0:
                for val in self.sensor_values:
                    request = requests.post(url=self.url_post, data = val)
                    self.sensor_values.remove(val)
                self.sensor_values = []
        except:
            self.sensor_values.append(metrics_json)
    
    def __del__(self):
        self.destroy()
    