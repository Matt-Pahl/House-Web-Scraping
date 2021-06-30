import boto3
from boto3.dynamodb.conditions import Key, Attr

ACCESS_KEY = ""
SECRET_KEY = ""

client = boto3.client('dynamodb', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name="us-east-2")


response = client.describe_table(TableName="House")

# dynamodb = boto3.resource('dynamodb', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name="us-east-2")


# table = dynamodb.Table('House')


# response = table.scan()