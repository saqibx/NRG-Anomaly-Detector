# NRG-Anomaly-Detector

A lightweight anomaly detection and monitoring system for energy devices, built using Python, InfluxDB, and Flask. The system ingests, stores, and visualizes real-time sensor data from multiple devices, and provides APIs for alerting and device management.

---

## Features

- **Device Data Ingestion:** Accepts time-series sensor data (voltage, current, temperature) from distributed energy devices via a secure API.
- **Real-time Storage:** Uses InfluxDB to efficiently store and query time-series data.
- **Anomaly Detection:** Leverages InfluxDB Flux Tasks to compute rolling z-scores and detect anomalies in device metrics, enabling real-time alerting.
- **Device & Alert APIs:** RESTful endpoints to retrieve device status, historical metrics, and active alerts.
- **Demo Data Generators:** Includes scripts to simulate device data and push it to the backend.
- **Extensible:** Easily adapts for additional sensors or alerting logic.

---

## Architecture Overview

```
[Devices/Sensors] --> [Flask API] --> [InfluxDB]
          ^                                |
          |                                v
     [Data Generator]              [Query/Alert APIs]
                                         |
                              [Flux Tasks: Rolling Z-Score]
                                         |
                                [Anomaly Detection & Alerts]
```

- Data is ingested through a Flask REST API (`/api/ingest`).
- Records are stored in InfluxDB (bucket: `energy_raw`).
- Device status and alerts are served via API endpoints.
- InfluxDB Flux Tasks run continuously to calculate rolling z-scores for each device's metrics, flagging anomalies and writing alerts to the `alerts` bucket.
- Example scripts generate and post simulated data.

---

## Anomaly Detection with Flux Tasks

The system employs [InfluxDB Flux Tasks](https://docs.influxdata.com/flux/v0.x/) to automatically compute rolling z-scores for device metrics (voltage, current, temperature). When a new data point's z-score exceeds a set threshold, an alert is generated and stored in a dedicated `alerts` bucket. This enables robust, real-time anomaly detection directly within the database engine, with no extra processing services required.

---

## Demo

I have developed a front end for this project, but I have chosen not to make it public at this time as it still needs some work. However, you can see a demonstration of the full system in action in the following YouTube video:

[![NRG-Anomaly-Detector Demo](https://img.youtube.com/vi/MJhV0BJgcig/0.jpg)](https://youtu.be/MJhV0BJgcig)

Or watch it here:

<a href="https://youtu.be/MJhV0BJgcig" target="_blank">
  <img src="https://img.youtube.com/vi/MJhV0BJgcig/0.jpg" alt="NRG-Anomaly-Detector Demo" width="480">
</a>

[https://youtu.be/MJhV0BJgcig](https://youtu.be/MJhV0BJgcig)

---

## Getting Started

### 1. Prerequisites

- Python 3.8+
- [InfluxDB 2.x](https://docs.influxdata.com/influxdb/v2.0/)
- Docker (optional, for running InfluxDB locally)

### 2. Clone the Repository

```bash
git clone https://github.com/saqibx/NRG-Anomaly-Detector.git
cd NRG-Anomaly-Detector
```

### 3. Setup InfluxDB (Local Development)

You can use the provided Docker Compose file:

```bash
cd InfluxDB
docker-compose up -d
```

Default credentials/configuration:
- **Org:** `saqib`
- **Bucket:** `energy_raw`
- **Username:** `admin`
- **Password:** `adminpass`
- **Token:** `dev-token`

### 4. Environment Variables

Create a `.env` file in the project root:

```
INFLUXDB_TOKEN=dev-token
INGEST_KEY=your_secret_key
```

Replace `your_secret_key` with a strong value for ingest API protection.

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```
*(Create `requirements.txt` with required packages: `flask`, `python-dotenv`, `influxdb-client`, `pydantic`, `flask-cors`, etc.)*

### 6. Run the Flask API

```bash
python app.py
```

---

## API Endpoints

### Ingestion

- `POST /api/ingest`
    - Accepts JSON or NDJSON payload of device readings.
    - Requires `Authorization` header matching `INGEST_KEY`.

**Example Payload:**
```json
{
  "device_id": 1001,
  "timeof": "2025-08-26T05:49:42+00:00",
  "voltage_v": 480.5,
  "current_a": 20.2,
  "temp_c": 40.1
}
```

### Devices

- `GET /api/devices`  
  Returns list of devices with last seen timestamp.
- `GET /api/devices/<device_id>`  
  Returns time-series data for a specific device.

### Alerts

- `GET /api/alerts`  
  Returns the latest alerts per device.

---

## Demo Data Generation

- **`data_script.py`**  
  Simulates device data and writes directly to InfluxDB.
- **`stream.py`**  
  Simulates device data and sends it through the Flask API, mimicking real device traffic.

Run either script in a separate terminal to populate the database with test data.

---

## Code Structure

- `app.py` &mdash; Main Flask API application.
- `QueryHelper.py` &mdash; Database helpers, InfluxDB queries, and Pydantic models.
- `data_script.py` &mdash; Direct InfluxDB data writer simulation.
- `stream.py` &mdash; API-based data stream simulation.
- `InfluxDB/docker-compose.yml` &mdash; InfluxDB deployment.

---

## Security

- Data ingestion is protected via a shared key (`INGEST_KEY` header).
- In production, ensure API and database access is secured and keys are kept secret.

---

## License

MIT License

---

## Acknowledgements

- [InfluxDB Python Client](https://github.com/influxdata/influxdb-client-python)
- [Flask](https://flask.palletsprojects.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [InfluxDB Flux Tasks](https://docs.influxdata.com/flux/v0.x/)

---

*For questions, open an issue or contact the maintainer.*
