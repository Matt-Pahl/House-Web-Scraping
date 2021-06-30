import boto3
import numpy as np
import pandas as pd

def df_to_table(df, table):
    """Updates a dynamodb table with rows from a DataFrame."""
    for row in df.to_dict('records'):
            table.put_item(Item=row)

def table_to_df(table):
    """Reads a dynamodb table into a DataFrame."""
    response = table.scan()
    df = pd.DataFrame(response["Items"])
    return df

# read access keys
filepath = r"D:\Documents\House Hunt\rootkey.csv"
access_keys = dict([l.strip().split("=") for l in open(filepath, "r").readlines()])
    
# connect to database, 
dynamodb = boto3.resource('dynamodb', aws_access_key_id=access_keys["AWSAccessKeyId"],
                          aws_secret_access_key=access_keys["AWSSecretKey"], region_name="us-east-2")
table = dynamodb.Table('House')

# dummy DataFrame (should be house data)
df = pd.DataFrame([{"HouseID": "123sexy", "price": 9999, "sqft": 1236},
                   {"HouseID": "555mynamejeff", "price": 6235, "sqft": 420},
                   {"HouseID": "99booty", "price": 2222, "sqft": 6969, "beds": 2}])

# clean up
df = df.fillna(value=-1)
num_cols = df.select_dtypes(include=np.number).columns
df[num_cols] = df[num_cols].astype(int)

# send DataFrame to table
df_to_table(df, table)

# read table to DataFrame
df = table_to_df(table)
