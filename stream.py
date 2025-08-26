import datetime
import os
import random
import time, requests, datetime as dt, pandas as pd, streamlit as st


from influxdb_client.client import influxdb_client
from dotenv import load_dotenv
from pydantic import BaseModel, conint, field_validator

load_dotenv()
token = os.environ.get("INFLUXDB_TOKEN")
from QueryHelper import Record, DBHandler
org = "saqib"
url = "http://localhost:8086"
header = os.getenv("INGEST_KEY")

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
MEASUREMENT = "energy"

bucket = "energy_raw"

counter = 0


while True:

    time.sleep(0.8)
    counter += 1

    '''
    InfluxDB Task limits:
    curr -> 30.0
    volt -> 490.
    temp -> 70.0
    '''
    device_num = random.randint(1000, 1019)
    power_num = random.uniform(12.5, 17.8)
    current_num = random.uniform(18.5, 32.5)
    voltage_num = random.uniform(475.3, 492.8)
    temp_num = random.uniform(60.7, 73.2)

    timern = datetime.datetime.now(datetime.timezone.utc)

    url = "http://127.0.0.1:5000/api/ingest"
    payload = {
        "device_id": device_num,
        "timeof": str(timern),
        "voltage_v": voltage_num,
        "current_a": current_num,
        "temp_c": temp_num

    }

    auth = {
        "Authorization": header
    }

    res = requests.post(url, json=payload, headers=auth)
    print(res.json(), device_num, "count: ", counter)




#     one = Record(device_id=device_num, timeof=datetime.datetime.now(datetime.timezone.utc), voltage_v=voltage_num, current_a=current_num, temp_c=temp_num)
#     handle = DBHandler(client=client, bucket=bucket, org=org, measurement=MEASUREMENT)
#     handle.push(record=one)
#
# client.close()

