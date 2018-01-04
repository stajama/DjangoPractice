from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.template import loader
from homepage.models import Weather
import requests
import json
import logging
import datetime
import bs4
import re
import random
from datetime import timezone as xTimezone

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- \
         %(message)s')
logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s- \
         %(message)s')   
logging.basicConfig(level=logging.WARNING, format=' %(asctime)s - %(levelname)s- \
         %(message)s')
logging.basicConfig(level=logging.ERROR, format=' %(asctime)s - %(levelname)s- \
         %(message)s')
logging.basicConfig(level=logging.CRITICAL, format=' %(asctime)s - %(levelname)s- \
         %(message)s')
logging.disable(logging.WARNING)

def home(request):
    '''returns homepage template. Calls NYTimes API for 5 top news articles.'''
    # TODO - pretty up html/css on page.

    contextDic = {}
    url = "https://api.nytimes.com/svc/topstories/v2/home.json"
    headInfo = {"api-key": "e9aec1ec7dca446d817bb0832ef71834"}
    newsRequest = requests.get(url, headInfo)
    newsRequest = newsRequest.text
    newsRequestDict = json.loads(newsRequest)
    counter = 0
    for i in range(0, 15, 3):
        data = newsRequestDict["results"][counter]
        counter += 1
        contextDic['news' + str(i)] = data['title']
        contextDic['news' + str(i + 1)] = data['abstract']
        contextDic['news' + str(i + 2)] = data['url']
    weatherInfo = getWeatherInfo()
    contextDic['weatherTemp'] = calculateFahrenheit(weatherInfo[0]) + "F"
    contextDic['weatherDesc'] = weatherInfo[1]
    contextDic['weatherCity'] = weatherInfo[2]
    contextDic['photo'] = getHumblePic()
    template = loader.get_template('homepage/home.html')
    return HttpResponse(template.render(contextDic, request))

def getWeatherInfo():
    '''Makes a call to the Open Weather API, returns a list: 
    [temperature, weather description, location].
    Call is only made if last call is at least 10 minutes past.'''

    # Get database info
    query = Weather.objects.all()
    # If the database if not empty, query for the latest api call.
    if query.exists():
        query = Weather.objects.order_by('id')
        query = query[len(query) - 1]
        # If latest API call is over 10 minutes ago, create a fresh API call,  
        # and add information to the database with datetime.now() timestamp.
        rightNow = datetime.datetime.now(xTimezone.utc)
        if (rightNow - query.api_call_time).seconds > 600:
            # API Call
            url = "http://api.openweathermap.org/data/2.5/forecast?id=4273837&APPID=9bf2228b6375f8753f9ced0f95ef8574"
            try:
                weatherRequest = requests.get(url)
            except requests.HTTPError():
                logging.ERROR("Weather API call has failed.")
                return [None, None, None]
            weatherInfo = json.loads(weatherRequest.text)
            weatherAdd = Weather(temperature=weatherInfo["list"][0]["main"]["temp"], 
                                 description=weatherInfo["list"][0]["weather"][0]["description"],
                                 location=weatherInfo["city"]["name"] + ', ' + weatherInfo["city"]["country"],
                                 api_call_time=timezone.now())
            weatherAdd.save()
            return [weatherAdd.temperature, weatherAdd.description, weatherAdd.location]
        else:
            # Else: use latest information available in database
            return [query.temperature, query.description, query.location]
    else:
        # Else: database is empty. An initial call to the weather API must be made
        url = "http://api.openweathermap.org/data/2.5/forecast?id=4273837&APPID=9bf2228b6375f8753f9ced0f95ef8574"
        try:
            weatherRequest = requests.get(url)
        except requests.HTTPError():
                logging.ERROR("Weather API call has failed.")
                return [None, None, None]
        weatherInfo = json.loads(weatherRequest.text)
        weatherAdd = Weather(temperature=weatherInfo["list"][0]["main"]["temp"], 
                             description=weatherInfo["list"][0]["weather"][0]["description"],
                             location=weatherInfo["city"]["name"] + ', ' + weatherInfo["city"]["country"],
                             api_call_time=timezone.now())
        weatherAdd.save()
        return [weatherAdd.temperature, weatherAdd.description, weatherAdd.location]

def getHumblePic():
    '''Finds random pick from recent pictures on hubblesite.org. Returns link
    to image as a string. Returns None if there is a problem.'''

    x = requests.get('http://hubblesite.org/images/gallery')
    soup = bs4.BeautifulSoup(x.text, 'lxml')
    pickList = []
    for i in soup.find_all('a'):
        if i.get('href') == None:
            continue
        if re.match(r'/image/\d{4}/', i.get('href')) != None:
            pickList.append("http://hubblesite.org" + i.get('href'))
    selected = pickList[random.randint(0, len(pickList) - 1)]
    x = requests.get(selected)
    soup = bs4.BeautifulSoup(x.text, 'lxml')
    for i in soup.find_all('a'):
        if 'http://imgsrc.' in i.get('href'):
            return i.get('href')
    logging.CRITICAL("getHumblePic --- Houston, we have a problem...")
    return

def calculateFahrenheit(tempString):
    '''Returns the string input in Kelvin as a string in Fahrenheit.)'''
    temp = float(tempString)
    print(temp)
    return str(round((temp * (9 / 5)) - 459.67, 2))