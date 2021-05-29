from bs4 import BeautifulSoup
from requests import get
import math
import pandas as pd
import itertools
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import date
sns.set()

#TODO have to set this to be able to callabe by zip code in a flask API request

headers = ({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
redfin = "https://www.redfin.com/zipcode/01028/filter/sort=lo-days"

response = get(redfin, headers=headers)
html_soup = BeautifulSoup(response.text, 'html.parser')
house_containers = html_soup.find_all('div', class_="bottomV2")
#try to see if there is stuff with more than one result set
try:
    totsale = int(re.findall("(?<=of\s).[0-9]*", html_soup.find_all('div', class_="homes summary")[0].text)[0])
except:
    totsale = int(re.findall("[0-9]+", html_soup.find_all('div', class_="homes summary")[0].text)[0])

addresses = []
prices = []
zipcode = []
beds = []
baths = []
sqfts = []
hrefs = []
total_houses_sale_time_loaded = []
time_loaded = []

list_of_all_houses = []

def breakdown_func(house_containers):
    y=0
    for house in house_containers:
        #break down the thigns further
        
        first = house_containers[y]
        stats = first.find_all('div', class_="stats")

        address = first.find_all('div', class_="homeAddressV2")[0].text
        addresses.append(address)

        price = first.find_all('span')[0].text
        prices.append(int(price.replace("$", "").replace(",", "")))

        bed = stats[0].text
        beds.append(bed)

        bath = stats[1].text
        baths.append(bath)

        sqft = stats[2].text
        sqfts.append(sqft)

        link = first.find_all('a', href=True)
        href = link[0]['href']
        hrefs.append('https://www.redfin.com/{}'.format(href))

        total_houses_sale_time_loaded.append(totsale)
        time_loaded.append(date.today())
        y=y+1

        temp = {'addresses': address, 'prices': price, 'beds':bed, 'baths':bath, 'sqfts':sqft, 'links': href, 'total_houses_sale_time_loaded':totsale, 'time_loaded':time_loaded.append(date.today())}
        list_of_all_houses.append(temp)
    return(1)

#redfin stores 41 per page
pages = math.ceil(totsale/41)
for x in range(1, pages+1):
    
    if x == 1:
        #don't worry about the extra link

        #turn this into a function where you pass the house_containers variable
        breakdown_func(house_containers)

    else:
        redfin = "{}/page-{}".format(redfin,x)

        response = get(redfin, headers=headers)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        house_containers = html_soup.find_all('div', class_="bottomV2")
        
        breakdown_func(house_containers)

df_all_houses = pd.DataFrame(list_of_all_houses)
df_all_houses.to_excel("temp.xlsx", index=False)
print('You scraped {} pages containing {} houses'.format(pages, totsale))
print(df_all_houses)

"""
cols = ['Address', 'ZipCode', 'Price', 'Size', 'Beds', 'Bath', 'Link', 'TimeLoaded', 'TotHousesSale']
houses = pd.DataFrame({'Address': addresses,
                            'ZipCode': zipcode, 
                            'Price': prices, 
                            'Size':sqfts, 
                            'Beds':beds, 
                            'Bath':baths, 
                            'Link':hrefs, 
                            'TimeLoaded':time_loaded, 
                            'TotHousesSale':total_houses_sale_time_loaded})[cols]
print(houses.head())
"""