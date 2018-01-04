import requests
import bs4
import re
import random

def getHumblePic():
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
    return

print(getHumblePic())