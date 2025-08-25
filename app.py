from QueryHelper import get_all_devices, get_device, Record, get_all_alerts ,DBHandler, bucket, MEASUREMENT
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

import json

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("INFLUXDB_TOKEN")
org = "saqib"
url = "http://localhost:8086"
INGEST_KEY = os.getenv("INGEST_KEY")
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

app = Flask(__name__)


#TODO: ADD GET /timeseries -> Returns chart
#TODO: ADD GET /alerts -> Anything in the Anomaly bucket


@app.route("/api/alerts", methods=['GET'])
def view_all_alerts():
    data = get_all_alerts()
    return jsonify(data)



@app.route("/api/devices")
def view_all_devices():
    data = get_all_devices()
    return jsonify(data)


@app.get("/api/devices/<device_id>")
def view_device(device_id):
    data = get_device(device_id)
    return data

@app.post("/api/ingest")
def ingest_information():

    auth_header = request.headers.get("Authorization")

    if auth_header != INGEST_KEY:
        return jsonify({"error":"Unauthorized Access, double check your headers"}), 401
    else:
        data = request.get_json(silent=True)
        items = []

        if data is None:
            # Handle raw text data (NDJSON format)
            raw = request.get_data(as_text=True)
            if not raw or not raw.strip():
                return jsonify({"ok": False, "error": "empty data"}), 400

            for line in raw.splitlines():
                line = line.strip()
                if line:
                    items.append(json.loads(line))
        else:
            # Handle JSON data
            items = data if isinstance(data, list) else [data]

        # Process the items
        try:
            records = [Record(**item) for item in items]
            print("INGEST DEBUG:", [r.model_dump() for r in records])
        except Exception as e:
            return jsonify({"ok": False, "error": "validation_error", "details": str(e)}), 422

        # Write to Influx
        try:
            with InfluxDBClient(url=url, token=token, org=org) as client:
                db = DBHandler(client, bucket=bucket, org=org, measurement=MEASUREMENT)
                print("INGEST DEBUG:", [r.model_dump() for r in records])

                for r in records:
                    db.push(r)
            return jsonify({"ok": True, "written": len(records)}), 200
        except Exception as e:
            return jsonify({"ok": False, "error": "write_failed", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)