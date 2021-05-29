import re
import pandas as pd
import matplotlib.pyplot as plt

from requests import get
from datetime import date
from bs4 import BeautifulSoup


_HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
_REDFIN_URL = "https://www.redfin.com/zipcode/{}/filter/sort=lo-days"


def extract_house_info(house):
    """Return info for a single house as a dict"""
    tmp = {}
    stats = house.find_all('div', class_="stats")
    tmp["beds"] = stats[0].text
    tmp["baths"] = stats[1].text
    tmp["sqft"] = stats[2].text
    
    tmp["address"] = house.find_all('div', class_="homeAddressV2")[0].text

    price = house.find_all('span')[0].text.replace(",", "")
    tmp["price"] = int(re.findall(r"(\d+)", price)[0])

    link = house.find_all('a', href=True)[0]['href']
    tmp["link"] = 'https://www.redfin.com{}'.format(link)
    tmp["time_loaded"] = date.today()
    return tmp


def get_houses(zipcode):
    """Return info for all houses in a zipcode as a DataFrame"""
    redfin = _REDFIN_URL.format(zipcode)
    response = get(redfin, headers=_HEADERS)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    house_containers = html_soup.find_all('div', class_="bottomV2")
    
    df = pd.DataFrame([extract_house_info(h) for h in house_containers])
    
    # remove land lots only
    if "sqft" in df.columns:
        df = df[~df["sqft"].str.contains("Lot")]
    
    # format values as numbers
    for c in ["sqft", "beds",  "baths"]:
        if c in df.columns:
            df.loc[:, c] = df[c].str.replace(",", "").copy()
            df.loc[:, c] = df[c].str.extract(r"(\d+\.?\d*)")[0].astype(float)
    
    # extract town, state, and zipcode
    if "address" in df.columns:
        cols = ["street", "town", "state", "zipcode"]
        pat = r"(.*), (\w+\s?\w*), (\w{2}) (\d+)$"
        df[cols] = df["address"].str.extract(pat)
    return df

# get houses for all these zipcodes
zipcodes = ["06082", "01028" ,"06078", "06071", "06035",
            "06096", "06006", "06095", "06088", "06074"]
df = pd.concat([get_houses(zc) for zc in zipcodes], ignore_index=True)

# indices of house with >= 3 beds, >=2 baths, <300000  price
igood = df["beds"].ge(3) & df["baths"].ge(2) & df["price"].lt(300000)

# plot price vs. total rooms (beds + baths)
df_good = df[igood].sort_values("price")
plt.plot(df_good["beds"] + df_good["baths"], df_good["price"], '.')






