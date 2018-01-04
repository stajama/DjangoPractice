from django.db import models

class Weather(models.Model):
    temperature = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    location = models.CharField(max_length=50)
    api_call_time = models.DateTimeField("called at")

    # def dumpInfo(self):
    #     # for shell DB testing
    #     return str({'temperature': self.temperature,
    #                 'description': self.description,
    #                 'location': self.location,
    #                 'called at': self.api_call_time})        
