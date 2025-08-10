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

# write_api = client.write_api(write_options=SYNCHRONOUS)
#
# for value in range(5):
#     point = (
#         Point("measurement1")
#         .tag("tagname1", "tagvalue1")
#         .field("field1", value)
#     )
#     write_api.write(bucket=bucket, org="saqib", record=point)
#     time.sleep(1)  # separate points by 1 second

query_api = client.query_api()

# query = """from(bucket: "energy_raw")
#  |> range(start: -10m)
#  |> filter(fn: (r) => r._measurement == "energy")
#  |> mean()"""



query = '''from(bucket: "energy_raw")
  |> range(start: -30m, stop: now())
  |> filter(fn: (r) => r._measurement == "energy" and r.device_id == "1002")
  |> filter(fn: (r) => r._field == "temp_c")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> group(columns: [])
  |> sort(columns: ["_time"])'''

tables = query_api.query(query, org="saqib")

# for table in tables:
#   for record in table.records:
#     print(record)

print(tables[0].records)
