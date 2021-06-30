import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
# from requests import get
from datetime import date
from bs4 import BeautifulSoup
from sklearn import metrics
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split


def normalized_hash(s):
    tmp = s.lower()
    tmp = re.sub(" #\d+", "", tmp)
    tmp = re.sub("unit [\d\w-]+", "", tmp)
    tmp = re.findall("([\S]+)", tmp)
    
    if len(tmp) <= 3:
        tmp = tmp[:2]
    if len(tmp) > 3:
        tmp = tmp[:3]

    return "".join(tmp)



_HEADERS = ({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
_REDFIN_URL_SELL = "https://www.redfin.com/zipcode/{}/filter/sort=lo-days"
_REDFIN_URL_SOLD = "https://www.redfin.com/zipcode/{}/filter/sort=lo-days,include=sold-1mo"


def extract_house_info(house):
    """Return info for a single house as a dict"""
    
    print(house)
    tmp = {}
    stats = house.find_all('div', class_="stats")
    tmp["beds"] = stats[0].text
    tmp["baths"] = stats[1].text
    tmp["sqft"] = stats[2].text
    
    # print(stats)
    
    tmp["address"] = house.find_all('div', class_="homeAddressV2")[0].text

    price = house.find_all('span')[0].text.replace(",", "")
    
    try:
        tmp["price"] = int(re.findall(r"(\d+)", price)[0])
    except Exception:
        tmp["price"] = -1

    link = house.find_all('a', href=True)[0]['href']
    tmp["link"] = 'https://www.redfin.com{}'.format(link)
    tmp["time_loaded"] = date.today()
    
    return tmp


def get_houses(zipcode, mode="sell"):
    """Return info for all houses in a zipcode as a DataFrame"""
    if mode == "sold":
        redfin = _REDFIN_URL_SOLD.format(zipcode)
    else:
        redfin = _REDFIN_URL_SELL.format(zipcode)
        
    response = requests.get(redfin, headers=_HEADERS)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    house_containers = html_soup.find_all('div', class_="bottomV2")
    
    print(html_soup)
    
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

# zipcodes = ["06082"]
mode = "sell"
df = pd.concat([get_houses(zc, mode) for zc in zipcodes], ignore_index=True)
df["HouseID"] = df["street"].apply(normalized_hash) + df["zipcode"]
df = df.drop_duplicates(subset="HouseID")

# drop None
df = df.dropna()

# only numbers greater than zero
num_cols = df.select_dtypes(include=np.number).columns
df = df[~df[num_cols].lt(0).any(axis=1)]


#%%






import boto3
import numpy as np
import pandas as pd
from boto3.dynamodb.conditions import Key


def df_to_table(df, table):
    """Updates a dynamodb table with rows from a DataFrame."""
    for row in df.to_dict('records'):
            table.put_item(Item=row)



filepath = r"D:\Documents\House Hunt\rootkey.csv"
access_keys = dict([l.strip().split("=") for l in open(filepath, "r").readlines()])
    
dynamodb = boto3.resource('dynamodb', aws_access_key_id=access_keys["AWSAccessKeyId"],
                          aws_secret_access_key=access_keys["AWSSecretKey"], region_name="us-east-2")

table = dynamodb.Table('House')

# only numbers greater than zero
num_cols = df.select_dtypes(include=np.number).columns
df[num_cols] = df[num_cols].astype(int)



df_to_table(df, table)








#%%

# indices of house with >= 3 beds, >=2 baths, <300000  price
igood = df["beds"].ge(3) & df["baths"].ge(2) & df["price"].lt(300000)

# plot price vs. total rooms (beds + baths)
df_good = df[igood].sort_values("price")
plt.plot(df_good["zipcode"], df_good["price"], '.')
plt.xticks(rotation=90)




#%%


df3 = df.to_dict('records')



#%%


df2 = df.drop_duplicates(["address"])



#%%

# Split dataset in features and target variable
feature_cols = ['beds', 'baths', 'sqft', 'town']
X = df[feature_cols] # Features
y = df["price"] # Target variable

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1) # 70% training and 30% test

# Create Decision Tree classifer object
clf = DecisionTreeClassifier()

# Train Decision Tree Classifer
clf = clf.fit(X_train, y_train)

# Predict the response for test dataset
y_pred = clf.predict(X_test)

# Model Accuracy, how often is the classifier correct?
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))