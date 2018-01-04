from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
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
    '''returns html for homepage. 5 top news stories from NYTimes API call.'''
    # TODO - pretty up html/css on page.

    url = "https://api.nytimes.com/svc/topstories/v2/home.json"
    headInfo = {"api-key": "e9aec1ec7dca446d817bb0832ef71834"}
    newsRequest = requests.get(url, headInfo)
    newsRequest = newsRequest.text
    newsRequestDict = json.loads(newsRequest)
    counter = 0
    for i in newsRequestDict["results"]:
        logging.debug("home - newsAPIParseCounter: " + str(counter))
        if counter >= 5:
            logging.info("Sanity Check - home View - newsAPIParseCounter > 5: " + str(counter))
            break
        else:
            logging.debug("Story " + str(counter) + " --- " + str(i))
            if counter == 0:
                article1 = [i["title"], i["abstract"], i["url"]]
            elif counter == 1:
                article2 = [i["title"], i["abstract"], i["url"]]
            elif counter == 2:
                article3 = [i["title"], i["abstract"], i["url"]]
            elif counter == 3:
                article4 = [i["title"], i["abstract"], i["url"]]
            elif counter == 4:
                article5 = [i["title"], i["abstract"], i["url"]]
            else:
                raise ValueError("newsAPIParseCounter has gone crazy...")
            counter += 1
    weatherInfo = getWeatherInfo()
    httpString = ''' <head>
                        <title>Mighty Mos Custom Homepage</title>
                    </head>
                    <h1>Mighty Mos Custom Homepage</h1>
                    
                    <p>
                        <b>Weather</b>
                    </p>
                    <p>
                         {15} --- {16} --- {17}
                    </p>
                    <p>
                        <b>News</b>
                    </p>
                    <p>
                        <a href="{2}">{0}\n</a><br />
                        {1}\n\n<br /><div></div>
                    </p> 
                    <p>
                        <a href="{5}">{3}\n</a><br />
                        {4}\n\n<br /><div></div>
                    </p>
                    <p>    
                        <a href="{8}">{6}\n</a><br />
                        {7}\n\n<br /><div></div>
                    </p>
                    <p>
                        <a href="{11}">{9}\n</a><br />
                        {10}\n\n<br /><div></div>
                    </p>
                    <p>
                        <a href="{14}">{12}\n</a><br />
                        {13}\n\n<br /><div></div>
                    </p>
                        
        <p>\n\n\n</p>
        <p>From the Hubble Space Telescope</p>
        <img  src="{18}">'''.format(
            article1[0], article1[1], article1[2], article2[0], article2[1], 
            article2[2], article3[0], article3[1], article3[2], article4[0], 
            article4[1], article4[2], article5[0], article5[1], article5[2],
            calculateFarenheit(weatherInfo[0]) + "&#176; F", weatherInfo[1], weatherInfo[2], getHumblePic())
    return HttpResponse(httpString)

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

def calculateFarenheit(tempString):
    '''Returns the string input in Kelvin as a string in Fahrenheit.)
    temp = float(tempString)
    print(temp)
    return str(round((temp * (9 / 5)) - 459.67, 2))