import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
# from requests import get
from datetime import date
from bs4 import BeautifulSoup
import json



import requests

from selenium.webdriver import Firefox
from time import sleep
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import json
from random import choice, randint
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.webdriver import FirefoxProfile



def get_page_selenium(driver, page_url):
    driver.get(page_url)
    html_text = driver.page_source
    return html_text



# filepath = r"D:\Documents\git\House-Web-Scraping\zillow_html_test2.html"
# url_text = open(filepath, "r").read()

_ZILLOW_URL = "https://www.zillow.com/homes/{}_rb/"



def zillow_to_df(zipcodes):
    """
    Return info for all houses in a zipcode or list of zipcodes as a DataFrame
    """
    if isinstance(zipcodes, str):
        zipcodes = [zipcodes]

    firefox_profile = FirefoxProfile()
    driver = Firefox(firefox_profile)
    driver.implicitly_wait(2)
    
    # get html content for each zipcode
    html_texts = []
    for zipcode in zipcodes:
        zillow = _ZILLOW_URL.format(zipcode)
        html_texts.append(get_page_selenium(driver, zillow))
    driver.quit()
    
    dfs = []
    for html_text in html_texts:
        html_soup = BeautifulSoup(html_text, 'html.parser')
        house_containers = html_soup.find_all('script')
        
        # ge all the houses
        houses = []
        for h in house_containers:
            if h.attrs.keys() >= {"type", "data-zrr-shared-data-key"}:
                if h.attrs["type"] == "application/json":
                    houses.append(h)
        
        # parse json to DataFrame
        if houses:
            json_text = re.findall("^<!--(.+)-->$", houses[0].string)[0]
            data = json.loads(json_text)
            rows = data["cat1"]["searchResults"]["listResults"]
            dfs.append(pd.DataFrame(rows))
            
    return pd.concat(dfs, ignore_index=True)

df = zillow_to_df(["06082", "01028"])

      