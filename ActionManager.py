import requests
from apscheduler.schedulers.background import BackgroundScheduler
import json
from json_logic import jsonLogic
from datetime import datetime

class ActionManager():
  
    def __init__(self, url_get = None):
        if url_get == None:
            self.url_get = 'http://localhost:50441/api/farms/4/ruleset'
        else:
            self.url_get = url_get
            
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
        
    def get_actions(self, currentDay, temperature, air_humidity, soil_humidity, watering=False):
        
        self.__save_metrics(temperature, air_humidity, soil_humidity)
        
        if watering == False:
            soil_humidity=None
        
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seconds = (now - midnight).seconds
        
        data = { 
            "currentTime" : seconds, 
            "currentDay" : currentDay,
            "soilHumidity": soil_humidity,
            "temperature" : temperature,
            "airHumidity" : air_humidity
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
        except requests.exceptions.RequestException as e:
            print(e)
    
    def __del__(self):
        self.destroy()
    
        

manager = ActionManager()
manager.destroy()

# ruleset example:
# '{"and":[{">":[{"var":"currentTime"},{"+":[800,{"*":[{"/":[{"var":"currentDay"},3]},10]}]}]},{"<":[{"var":"currentTime"},{"-":[2400,{"*":[{"/":[{"var":"currentDay"},3]},10]}]}]}]}'