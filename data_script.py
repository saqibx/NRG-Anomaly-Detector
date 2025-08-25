import random

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("INFLUXDB_TOKEN")
org = "saqib"
url = "http://localhost:8086"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket = "energy_raw"

write_api = client.write_api(write_options=SYNCHRONOUS)

count = 0
while True:
    time.sleep(1)
    device_num = random.randint(1000,1009)
    power_num = random.uniform(12.5, 17.8)
    current_num  = random.uniform(18.5,32.5)
    voltage_num = random.uniform(475.3,482.8)
    temp_num = random.uniform(34.7,43.2)

    point = (
        Point("energy")
        .tag("device_id", device_num)
        .tag("site","SITE A")
        .field("power_kw", power_num)
        .field("current_a", current_num)
        .field("voltage_v",voltage_num)
        .field("temp_c",temp_num)
    )
    write_api.write(bucket=bucket, org="saqib", record=point)
    count+=1
    print(f"record: {count}\n{device_num} |{power_num} | {voltage_num} | {current_num} | {temp_num}")



