"""Small analysis helpers for the ITC560 greenhouse notebook."""

from __future__ import annotations

import csv
from pathlib import Path


NUMERIC_COLUMNS = [
    "air_temperature_c",
    "relative_humidity_pct",
    "soil_moisture_pct",
    "light_lux",
    "co2_ppm",
    "water_flow_lpm",
    "gateway_latency_ms",
    "packet_loss_pct",
    "gateway_rssi_dbm",
    "device_battery_pct",
]


def load_rows(path: str | Path) -> list[dict]:
    """Load greenhouse sensor rows from a CSV file."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def numeric_summary(rows: list[dict], columns: list[str] | None = None) -> dict:
    """Return min, max, and average values for numeric sensor columns."""
    selected_columns = columns or NUMERIC_COLUMNS
    summary = {}

    for column in selected_columns:
        values = []
        for row in rows:
            value = row.get(column)
            # Some IoT readings are missing. Skip blanks before converting to float.
            if value in ("", None, "nan", "NaN"):
                continue
            values.append(float(value))
        if not values:
            continue
        summary[column] = {
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(sum(values) / len(values), 2),
        }

    return summary


def count_anomalies(rows: list[dict]) -> dict[str, int]:
    """Count normal and abnormal labelled events in the dataset."""
    counts: dict[str, int] = {}
    for row in rows:
        label = row.get("anomaly_label", "unknown")
        counts[label] = counts.get(label, 0) + 1
    return counts


def identify_risk_windows(rows: list[dict]) -> list[dict]:
    """Find rows where environmental and network symptoms occur together."""
    risk_rows = []
    for row in rows:
        high_temperature = float(row["air_temperature_c"]) > 27
        has_soil_reading = row.get("soil_moisture_pct") not in ("", None)
        low_soil = has_soil_reading and float(row["soil_moisture_pct"]) < 42
        high_co2 = float(row["co2_ppm"]) > 560
        high_packet_loss = float(row["packet_loss_pct"]) > 2
        high_latency = float(row["gateway_latency_ms"]) > 140
        network_degraded = high_packet_loss or high_latency
        missing_sensor = row.get("sensor_status") != "ok"

        if (high_temperature or high_co2) and (low_soil or network_degraded or missing_sensor):
            risk_rows.append(row)
    return risk_rows
