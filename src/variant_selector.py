"""Select and generate a reproducible greenhouse IoT dataset variant."""

from __future__ import annotations

import csv
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELECTED_DIR = ROOT / "data" / "selected"
MANIFEST_PATH = SELECTED_DIR / "variant_manifest.json"

VARIANTS = [
    {
        "id": "greenhouse-a",
        "name": "Cool coastal greenhouse",
        "temperature_offset": -1.5,
        "humidity_offset": 6.0,
        "soil_offset": 3.0,
        "fault_window": (34, 40),
        "gateway_window": (118, 124),
        "dropout_window": (82, 84),
        "fault_zone": "north-bed",
    },
    {
        "id": "greenhouse-b",
        "name": "Warm inland greenhouse",
        "temperature_offset": 2.0,
        "humidity_offset": -5.0,
        "soil_offset": -4.0,
        "fault_window": (48, 55),
        "gateway_window": (96, 102),
        "dropout_window": (132, 134),
        "fault_zone": "south-bed",
    },
    {
        "id": "greenhouse-c",
        "name": "High-yield research greenhouse",
        "temperature_offset": 0.5,
        "humidity_offset": 2.0,
        "soil_offset": 6.0,
        "fault_window": (72, 78),
        "gateway_window": (34, 39),
        "dropout_window": (108, 110),
        "fault_zone": "north-bed",
    },
    {
        "id": "greenhouse-d",
        "name": "Water-constrained greenhouse",
        "temperature_offset": 1.2,
        "humidity_offset": -8.0,
        "soil_offset": -9.0,
        "fault_window": (90, 96),
        "gateway_window": (142, 148),
        "dropout_window": (44, 46),
        "fault_zone": "south-bed",
    },
]

ZONES = [
    {
        "id": "north-bed",
        "temperature_adjust": 0.4,
        "humidity_adjust": -1.5,
        "soil_adjust": -1.0,
        "light_adjust": 70,
    },
    {
        "id": "south-bed",
        "temperature_adjust": -0.3,
        "humidity_adjust": 1.2,
        "soil_adjust": 2.0,
        "light_adjust": -40,
    },
]


def select_variant() -> dict:
    """Return the existing selected variant, or create one if needed."""
    SELECTED_DIR.mkdir(parents=True, exist_ok=True)
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    variant = random.choice(VARIANTS).copy()
    variant["selected_at_utc"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    variant["dataset_file"] = f"{variant['id']}_sensor_readings.csv"
    MANIFEST_PATH.write_text(json.dumps(variant, indent=2) + "\n", encoding="utf-8")
    return variant


def generate_dataset(variant: dict) -> Path:
    """Generate the selected greenhouse dataset if it does not already exist."""
    dataset_path = SELECTED_DIR / variant["dataset_file"]
    if dataset_path.exists():
        return dataset_path

    rng = random.Random(variant["id"])
    start = datetime(2026, 9, 21, 0, 0)
    fault_start, fault_end = variant["fault_window"]
    gateway_start, gateway_end = variant["gateway_window"]
    dropout_start, dropout_end = variant["dropout_window"]
    rows = []

    for hour in range(7 * 24):
        timestamp = start + timedelta(hours=hour)
        day_cycle = (hour % 24) / 24
        daylight = max(0, 1 - abs(day_cycle - 0.54) * 2.35)
        door_open = 1 if hour % 37 in (0, 1) else 0
        base_latency = 80 + rng.randint(-12, 18)
        base_packet_loss = max(0, rng.gauss(0.7, 0.4))
        gateway_degraded = gateway_start <= hour <= gateway_end

        for zone in ZONES:
            temp = 18.5 + variant["temperature_offset"] + zone["temperature_adjust"] + 7.5 * daylight
            humidity = 69 + variant["humidity_offset"] + zone["humidity_adjust"] - 13 * daylight
            soil = 51 + variant["soil_offset"] + zone["soil_adjust"] - 0.075 * hour
            light = max(0, 980 * daylight + zone["light_adjust"])
            co2 = 430 + 110 * daylight + rng.randint(-18, 28)
            battery = 94 - (0.055 * hour) - (1.2 if zone["id"] == "south-bed" else 0)
            rssi = -58 - rng.randint(0, 12) - (5 if zone["id"] == "south-bed" else 0)
            latency = base_latency + (8 if zone["id"] == "south-bed" else 0)
            packet_loss = base_packet_loss
            anomaly = "normal"
            sensor_status = "ok"

            if fault_start <= hour <= fault_end and zone["id"] == variant["fault_zone"]:
                temp += 4.5
                humidity -= 10
                co2 += 95
                anomaly = "ventilation_fault"

            irrigation_needed = soil < 43
            irrigation = 1 if irrigation_needed and hour % 6 == 0 else 0
            if irrigation_needed and fault_start <= hour <= fault_end and zone["id"] != variant["fault_zone"]:
                irrigation = 0
                anomaly = "irrigation_gap"
            if irrigation:
                soil += 5.5
            water_flow = round(rng.uniform(4.8, 6.2), 2) if irrigation else 0.0
            fan = 1 if temp > 25.5 or co2 > 540 else 0

            if gateway_degraded:
                latency += 90
                packet_loss += 3.2
                rssi -= 10
                if anomaly == "normal":
                    anomaly = "gateway_degraded"

            missing_soil = dropout_start <= hour <= dropout_end and zone["id"] == variant["fault_zone"]
            missing_light = hour in (27, 111) and zone["id"] != variant["fault_zone"]
            if missing_soil or missing_light:
                sensor_status = "missing_reading"
                if anomaly == "normal":
                    anomaly = "sensor_dropout"

            rows.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "zone": zone["id"],
                    "air_temperature_c": round(temp + rng.uniform(-0.5, 0.5), 2),
                    "relative_humidity_pct": round(humidity + rng.uniform(-1.5, 1.5), 2),
                    "soil_moisture_pct": "" if missing_soil else round(soil + rng.uniform(-1.0, 1.0), 2),
                    "light_lux": "" if missing_light else round(light + rng.uniform(-25, 25), 2),
                    "co2_ppm": round(co2, 2),
                    "door_open": door_open,
                    "fan_active": fan,
                    "irrigation_active": irrigation,
                    "water_flow_lpm": water_flow,
                    "gateway_latency_ms": round(latency, 2),
                    "packet_loss_pct": round(packet_loss, 2),
                    "gateway_rssi_dbm": round(rssi, 2),
                    "device_battery_pct": round(max(20, battery + rng.uniform(-0.8, 0.8)), 2),
                    "sensor_status": sensor_status,
                    "anomaly_label": anomaly,
                }
            )

    with dataset_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return dataset_path


def main() -> None:
    variant = select_variant()
    dataset_path = generate_dataset(variant)
    print(f"Selected variant: {variant['id']} - {variant['name']}")
    print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"Dataset: {dataset_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
