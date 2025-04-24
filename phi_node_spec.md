# Φ-Feedback Node Specification

## Purpose
The Φ-Feedback Node captures real-time environmental data to compute local entropy–flux ratios (Φ), enabling recursive stabilization of ecological gradients.

## Core Sensors
- Temperature
- Humidity / Soil moisture
- CO₂ concentration
- Light intensity (optional)
- GPS location

## Hardware Stack
- Microcontroller: ESP32 / Raspberry Pi Pico W
- Sensor Suite: DHT22 / SCD30 / Capacitive Moisture Sensor
- Power: Rechargeable Li-ion with solar option
- Connectivity: LoRa / Wi-Fi (fallback to SD logging if offline)

## Output Schema
Each node broadcasts the following JSON packet every 60s:
```json
{
  "node_id": "phi-017",
  "timestamp": "2025-04-24T16:00:00Z",
  "gps": [51.2194, 4.4025],
  "temperature_c": 22.3,
  "co2_ppm": 413,
  "soil_moisture": 0.78,
  "phi": 0.19
}
