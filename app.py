from symbol import pass_stmt

from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

#TODO: ADD GET /devices -> Returns all active devices that have reported in the last 24 hours
#TODO: ADD GET /timeseries -> Returns chart
#TODO: ADD GET /alerts -> Anything in the Anomaly bucket
#TODO: ADD GET /ingest -> So our program can ingest new data

@app.route("/devices")
def view_devices():
    pass


if __name__ == "__main__":
    app.run(debug=True)
