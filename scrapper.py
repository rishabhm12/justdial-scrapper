import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import pandas as pd
import os


def get_rating(body):
    rating = 0.0
    text = body.find('span', {'class':'star_m'})
    if text is not None:
        for item in text:
            rating += float(item['class'][0][1:])/10

    return rating

def get_rating_count(body):
    text = body.find('span', {'class':'rt_count'}).string

    # Get only digits
    rating_count =''.join(i for i in text if i.isdigit())
    return rating_count


def innerHTML(element):
    return element.decode_contents(formatter="html")

def get_address(body):
    return body.find('span', {'class':'mrehover'}).text.strip()


def get_name(body):
    return body.find('span', {'class':'jcn'}).a.string
#  return body.find('span', {'class':'nlogo lazy srtbyPic'})

def get_geocodes(body):
    wd = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"))
    geo_url = service_html.find('span', {'class':'jcn'}).a['href']
    wd.get(geo_url)
    wd.execute_script('''
    (function(open) {
        window.XMLHttpRequest.prototype.open = function() {
            this.addEventListener("readystatechange", function() {
                if(this.readyState == 4 && this.responseURL.indexOf('maps.php') > -1){
                    window.latlong = this.responseText
                }
            }, false);
            open.apply(this, arguments);
        };
    })(window.XMLHttpRequest.prototype.open);
    ''')

    
    try:
        wd.find_element_by_xpath('//a[@class="mapicn"]').click()
        geocode = wd.execute_async_script('var theData = arguments[0]; theData(latlong)')
    except:
        print("Element not found")
        lat = None
        lon = None
        wd.close()
        return lat, lon, geo_url
    
    geocode = json.loads(geocode)
    lat, lon = float(geocode['lil']), float(geocode['lon'])
    wd.close()
    
    return lat, lon , geo_url

grocery_stores = pd.DataFrame()

page_number = 12
while (page_number <= 50):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
    url = "https://justdial.com/Bangalore/Supermarkets/nct-10463784/page-%s" % (page_number)
    
    request = requests.get(url, headers = headers)
    soup = BeautifulSoup(request.text, 'html.parser')
    services = soup.find_all('li', {'class': 'cntanr'})
    
    for service_html in services:
        name = get_name(service_html)
        rating = get_rating(service_html)
        count = get_rating_count(service_html)
        address = get_address(service_html)
        lat, lon , geo_url = get_geocodes(service_html)
        grocery_stores = grocery_stores.append({'store_name':name,'address':address,'rating':rating,'rating_count':count,
                                               'latitude':lat,'longitude':lon, 'url':geo_url},
                                               ignore_index = True)
    page_number += 1
    print(f"****** Completed page {page_number} *********")


grocery_stores.to_csv('bengaluru_super_markets.csv', index = False)
         


