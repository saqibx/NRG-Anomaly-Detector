import json
from datetime import datetime, timezone
from typing import Dict

import influxdb_client, os, time
from flask import jsonify
from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
from pydantic import BaseModel, conint, field_validator

load_dotenv()
token = os.environ.get("INFLUXDB_TOKEN")
org = "saqib"
url = "http://localhost:8086"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
MEASUREMENT = "energy"

bucket = "energy_raw"
query_api = client.query_api()

class Record(BaseModel):
    device_id: conint(gt=999)
    timeof: datetime
    voltage_v: float
    current_a: float
    temp_c: float

    @field_validator("timeof",mode="before")
    @classmethod
    def convert_utc(cls,v):
        if isinstance(v, str):
            v = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

class DBHandler:
    def __init__(self, client: InfluxDBClient, bucket: str, org: str, measurement: str = MEASUREMENT):
        self.client = client
        self.bucket = bucket
        self.org = org
        self.measurement = measurement

    def _ensure_aware_utc(self, dt: datetime) -> datetime:
        # Make the datetime timezone-aware in UTC
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def push(self, record: Record) -> None:
        ts = self._ensure_aware_utc(record.timeof)

        # One point with multiple fields (same timestamp, same tags)
        point = (
            Point(self.measurement)
            .tag("device_id", str(record.device_id))
            .field("voltage_v", float(record.voltage_v))
            .field("current_a", float(record.current_a))
            .field("temp_c",   float(record.temp_c))
            .time(ts)
        )

        # write_api = self.client.write_api(write_options=WriteOptions(batch_size=1))
        # write_api.write(bucket=self.bucket, org=self.org, record=point)
        with self.client.write_api(write_options=SYNCHRONOUS) as w:
            w.write(bucket=self.bucket, org=self.org, record=point)


def get_all_devices():
    devices = []
    query = '''
     from(bucket: "energy_raw")
     |> range(start: -10h)
     |> filter(fn: (r) => r._measurement == "energy")
     |> group(columns: ["device_id"])
     |> last()
     |> keep(columns: ["device_id", "_time"])
    '''

    tables = query_api.query(query, org="saqib")
    for result in tables:
        for record in result.records:
            devices.append({
                "device_id": record['device_id'],
                "last_seen": record['_time'].isoformat()
            })



    return devices


def get_device(device_id):
    client = InfluxDBClient(url=url, token=token, org=org)
    q = client.query_api()
    WINDOWS = {
        "10m": "5s",  # ~120 pts
        "1h": "1m",  # ~60 pts
    }
    METRICS = ["voltage_v", "temp_c", "current_a"]
    UNITS = {"voltage": "V", "temperature": "°C", "current": "A"}
    series = {m: {} for m in METRICS}

    for metric in METRICS:
        for win, every in WINDOWS.items():
            flux = f'''
                from(bucket:"energy_raw")
                  |> range(start:-{win})
                  |> filter(fn:(r)=> r["_measurement"]=="energy")
                  |> filter(fn:(r)=> r["device_id"]=="{device_id}")
                  |> filter(fn:(r)=> r["_field"]=="{metric}")
                  |> aggregateWindow(every: {every}, fn: mean, createEmpty: false)
                  |> yield(name:"{metric}_{win}")
                '''
            pts = []
            for table in q.query(flux):
                for rec in table.records:
                    pts.append([int(rec.get_time().timestamp() * 1000), rec.get_value()])
            series[metric][win] = pts

    return jsonify({
        "device_id": device_id,
        "windows": list(WINDOWS.keys()),
        "metrics": METRICS,
        "units": UNITS,
        "series": series
    })


def get_all_alerts():
    query = '''
         from(bucket: "alerts")
         |> range(start: -24h)
         |> filter(fn: (r) => 
            r._measurement == "alerts" and
            r._field == "value"
         )
         |> group(columns: ["device_id", "reason"])   // one group with both keys
         |> sort(columns: ["_time"], desc: true)      // make “latest” explicit
         |> limit(n: 1)                                // latest per (device_id, reason)
         |> keep(columns: ["device_id", "reason", "_time", "_value"])
        '''
    devices = []
    tables = query_api.query(query, org="saqib")
    for result in tables:
        for record in result.records:
            devices.append({
                "device_id": record['device_id'],
                "reason": record["reason"],
                "last_seen": record['_time'].isoformat(),
                "value": record["_value"]
            })

    return devices