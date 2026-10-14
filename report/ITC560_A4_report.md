
# ITC560 Assessment 4 Report

Student Name: Asim Aijaz
Student ID: 11885852
GitHub Username: asimaijaz
Private Repository URL: https://github.com/asimaijaz/202660-itc560-a4-asimaijaz
Selected Dataset Variant: greenhouse-d (Water-constrained greenhouse)

## 1. Scenario And Dataset Variant

The dataset selected for this assessment is `greenhouse-d`, which represents a water-constrained greenhouse environment. In this operational setting, irrigation water supply is limited and crops face higher baseline evaporation and drought stress. Because water cannot be wasted through continuous open-loop watering, the greenhouse relies on soil moisture, temperature, humidity, light, and CO2 sensors across its growing beds to trigger irrigation and ventilation only when needed. At the same time, because soil moisture is already naturally low in this scenario, any delay or failure in irrigation control creates an immediate risk of crop wilting.

When `src/variant_selector.py` was executed, it generated the manifest file `data/selected/variant_manifest.json` and the dataset `data/selected/greenhouse-d_sensor_readings.csv` (recorded at `2026-10-14T04:20:13+00:00`). Keeping the manifest file in the repository is essential because it locks in the exact simulation parameters and fault windows assigned to this repository, allowing the marker to reproduce the exact same dataset and verify all calculations. For `greenhouse-d`, the manifest records a temperature offset of +1.2 C, a relative humidity offset of -8.0%, and a soil moisture offset of -9.0%, with a primary fault zone in `south-bed` (rows 90 to 96), a sensor dropout window (rows 44 to 46), and a gateway degradation window (rows 142 to 148).

## 2. Data Preparation And Quality

The dataset contains 336 hourly records collected over seven days from 21 September 2026 (00:00:00) to 27 September 2026 (23:00:00). The records are split evenly between two greenhouse zones, with 168 rows for `north-bed` and 168 rows for `south-bed`. The columns cover environmental sensor readings (`air_temperature_c`, `relative_humidity_pct`, `soil_moisture_pct`, `light_lux`, `co2_ppm`), actuator states and water flow (`door_open`, `fan_active`, `irrigation_active`, `water_flow_lpm`), device and network health metrics (`gateway_latency_ms`, `packet_loss_pct`, `gateway_rssi_dbm`, `device_battery_pct`, `sensor_status`), and an `anomaly_label` column.

During data exploration and quality checking in the notebook, two main data quality issues were found:

First, there are 5 missing values (`NaN`) in total, all occurring during rows marked with `sensor_status = missing_reading` and `anomaly_label = sensor_dropout`. Specifically, `soil_moisture_pct` is missing for 3 consecutive hours in `south-bed` on 22 September 2026 at 20:00, 21:00, and 22:00 (rows 89, 91, and 93). In addition, `light_lux` has 2 missing values in `north-bed` on 22 September at 03:00 (row 54) and 25 September at 15:00 (row 222).

Second, summary statistics showed a minimum `light_lux` reading of -22.33 lux. Because light intensity cannot physically be negative, I filtered the dataset for `light_lux < 0` and found 14 negative readings between -2.40 lux and -22.33 lux. All 14 negative values occurred in `south-bed` at night (between 23:00 and 03:00), and in every case the `sensor_status` column still reported `ok`. This shows that the light sensor in `south-bed` has a zero-point calibration drift that the basic device status check fails to detect.

To handle these issues safely without hiding operational risks, I kept the original raw columns intact for the risk indicator checks so that missing soil moisture readings (`NaN`) would still trigger `water_stress` and `device_health_risk`. In a water-constrained greenhouse, the controller cannot assume the soil has enough water when the sensor drops out. For continuous trend analysis, I created separate cleaned columns (`light_lux_clean` and `soil_moisture_clean`) where negative light values were replaced with `NA` and missing values were filled using linear interpolation grouped by `zone`, ensuring `north-bed` and `south-bed` readings were never mixed.

## 3. Analytics Results

The notebook analysis produced five output files in the `outputs/` folder: `greenhouse_risk_windows.csv` (which filtered 301 rows having at least one active risk condition), `greenhouse_zone_summary.csv`, `temperature_by_zone.png`, `gateway_latency_over_time.png`, and a custom chart `soil_moisture_irrigation_behaviour.png`.

In addition to the starter indicators (`thermal_risk`, `water_stress`, `air_quality_risk`, `network_degraded`, `device_health_risk`, `actuator_mismatch`, and `edge_action_priority`), I added two new indicators tailored to the `greenhouse-d` scenario:
1. `severe_water_stress`: Triggered when `soil_moisture_pct` drops below 35.0% (or is missing) while `irrigation_active == 0`.
2. `calibration_drift_risk`: Triggered when `light_lux < 0` while `sensor_status == 'ok'`.

The table below summarises the average sensor readings, risk counts, and anomaly labels across both zones from `outputs/greenhouse_zone_summary.csv` and the notebook outputs:

| Metric or Indicator | north-bed (168 hrs) | south-bed (168 hrs) | Combined Total (336 hrs) |
| --- | --- | --- | --- |
| Mean Air Temperature (C) | 23.35 | 22.77 | 23.06 (Min 18.99, Max 27.98) |
| Mean Relative Humidity (%) | 53.90 | 56.33 | 55.12 (Min 45.27, Max 63.62) |
| Mean Soil Moisture (%) | 35.60 | 38.53 | 37.05 (Min 27.61, Max 48.05) |
| Mean CO2 (ppm) | 482.85 | 485.70 | 484.27 (Min 413.0, Max 585.17) |
| Mean Gateway Latency (ms) | 86.95 | 94.95 | 90.95 (Min 68.0, Max 191.0) |
| Mean Gateway RSSI (dBm) | -64.58 | -69.58 | -67.08 (Min -82.0, Max -58.0) |
| thermal_risk (>27 C or <18 C) | 15 | 3 | 18 |
| water_stress (<42% or NaN) | 157 | 129 | 286 |
| severe_water_stress (<35% & irrigation off) | 74 | 42 | 116 |
| air_quality_risk (CO2 > 560 ppm) | 0 | 4 | 4 |
| network_degraded (latency >140 ms or loss >2%) | 7 | 7 | 14 |
| device_health_risk (RSSI <-72 dBm or dropout) | 6 | 48 | 54 |
| calibration_drift_risk (light < 0 & status ok) | 0 | 14 | 14 |
| actuator_mismatch | 142 | 118 | 260 |
| edge_action_priority | 9 | 36 | 45 |
| Anomaly counts | irrigation_gap: 7, sensor_dropout: 2, gateway_degraded: 7 | ventilation_fault: 7, sensor_dropout: 3, gateway_degraded: 7 | normal: 303, anomalies: 33 |

The visual outputs highlight how these indicators connect across sensors, actuators, and the network:

1. `outputs/soil_moisture_irrigation_behaviour.png`: This chart compares `soil_moisture_pct` over time in both zones against the 42% water stress line, the 35% severe water stress line, and green scatter points marking when `irrigation_active == 1`. It shows that `north-bed` stays below 42% moisture for 157 out of 168 hours and drops below 35% without irrigation for 74 hours. Even when soil moisture falls to 27.61% on 27 September or during the 7-hour `irrigation_gap` on 24 to 25 September (18:00 to 00:00, moisture 33.23% to 35.24%), the irrigation valve remains off (`0`), resulting in 142 hours of `actuator_mismatch` in `north-bed` and 118 hours in `south-bed`.
2. `outputs/temperature_by_zone.png`: This plot shows daily temperature cycles against the 27.0 C high-temperature threshold. `north-bed` is warmer overall and exceeds 27.0 C for 15 hours during midday peaks. However, `south-bed` shows an unusual evening spike to 27.80 C on 24 September at 18:00 during the `ventilation_fault` window, which also pushes `co2_ppm` up to 585.17 ppm (breaching the 560 ppm air quality threshold for 4 hours).
3. `outputs/gateway_latency_over_time.png`: This plot shows that average gateway latency normally sits between 68 ms and 110 ms, but spikes sharply above the 140 ms threshold for 7 consecutive hours from 26 September 22:00 to 27 September 04:00 (`gateway_degraded`). During this window, latency reaches 191.0 ms and packet loss rises to 4.54% across both zones.

## 4. Operational Interpretation

Comparing the two zones shows that `north-bed` and `south-bed` suffer from different operational problems that require targeted actions.

In `north-bed`, the primary operational risk is chronic under-irrigation and drought stress. With the -9.0% soil moisture offset in `greenhouse-d`, `north-bed` averages just 35.60% soil moisture and experiences 157 hours of `water_stress` and 74 hours of `severe_water_stress`. The most urgent window in `north-bed` occurs during the `irrigation_gap` from 24 September 18:00 to 25 September 00:00 (where soil moisture sits between 33.23% and 35.24% with zero irrigation flow) and again on 27 September between 00:00 and 04:00 when moisture drops to the dataset minimum of 27.61%. Because `actuator_mismatch` is triggered for 142 hours in `north-bed`, the existing irrigation control logic is either configured with a threshold far below crop requirements or commands are failing to reach the valve actuator.

In `south-bed`, the primary operational risk is poor device health, sensor reliability, and ventilation failure, creating a strong need for local edge control. `south-bed` triggers `device_health_risk` for 48 hours (compared to only 6 hours in `north-bed`), mainly because its wireless signal (`gateway_rssi_dbm`) averages -69.58 dBm and repeatedly drops below -72 dBm (down to -82.0 dBm), alongside the 3 consecutive hours of missing soil moisture readings on 22 September from 20:00 to 22:00 (`sensor_dropout`) and 14 hours of negative light readings (`calibration_drift_risk`). In addition, `south-bed` experiences a 7-hour `ventilation_fault` from 24 September 18:00 to 25 September 00:00, where temperature reaches 27.80 C and CO2 climbs to 585.17 ppm. Even though `fan_active` reports `1` during the first four hours of that fault, heat and CO2 continue to accumulate before the fan turns off at 22:00, pointing to a physical fan obstruction or damper failure rather than a simple software state issue.

Finally, the 7-hour `gateway_degraded` window from 26 September 22:00 to 27 September 04:00 affects both zones simultaneously (14 rows total). During this period, high latency (up to 191 ms) and packet loss (up to 4.54%) overlap with severe soil dryness (27.61% in `north-bed` and 32.22% in `south-bed`). Overall, `south-bed` records 36 hours of `edge_action_priority` and `north-bed` records 9 hours. This confirms that relying on a distant cloud server to make real-time irrigation or fan decisions is unsafe when gateway link quality degrades at the exact same time crops are experiencing environmental stress.

## 5. Platform And Data-Management Requirements

To manage the `greenhouse-d` environment reliably, the IoT platform should use a three-layer edge-to-cloud data architecture covering collection, validation, storage, processing, and operator dashboards:

1. Data Collection and Edge Validation: Sensor nodes in `north-bed` and `south-bed` should sample environmental metrics every 5 to 15 minutes and send readings to a local greenhouse gateway. Because `south-bed` suffers from weak RSSI (-82 dBm), placing a local repeater or using sub-GHz radio links is necessary to improve signal margin. Before the gateway passes data to the control loop or the cloud, an automated validation service at the edge should check physical bounds. Any `light_lux < 0` reading must be flagged as `calibration_drift_risk` and clamped to 0.0 lux for analytics, rather than trusting `sensor_status == 'ok'`. Similarly, when `soil_moisture_pct` reports `NaN` (such as the 3-hour dropout on 22 September), the gateway should log a sensor fault and use bounded short-term interpolation from recent moisture and `water_flow_lpm` records while restricting irrigation to safe, short fallback pulses.
2. Local Buffering and Cloud Storage: To prevent data loss during the `gateway_degraded` window (where packet loss hits 4.54% and latency hits 191 ms), the local gateway needs a store-and-forward buffer (such as a local SQLite queue or InfluxDB Edge instance) that stores readings locally and retries transmission over MQTT (`QoS 1`) once the network recovers. In the cloud, validated time-series telemetry should be stored in a time-series database (such as InfluxDB or AWS Timestream) partitioned by `zone` and `timestamp`, while device metadata, threshold settings, and the `variant_manifest.json` record are kept in a relational database for auditing.
3. Processing and Dashboard Services: Time-critical control rules (`water_stress`, `severe_water_stress`, `thermal_risk`, and `edge_action_priority`) must run locally on the edge gateway so that irrigation valves and ventilation fans operate without waiting for cloud round-trips. Furthermore, when the system sets `fan_active = 1` or `irrigation_active = 1`, the gateway should verify that `water_flow_lpm` increases or `co2_ppm` and temperature begin to drop within 15 to 30 minutes; if not, it should raise a physical actuator fault alert (catching the 24 September `ventilation_fault`). A dashboard service (such as Grafana) should display zone comparison charts, highlight the 301 risk-window records, and alert staff when `actuator_mismatch` or `calibration_drift_risk` occurs.

## 6. Hardware Suitability

Choosing hardware for this greenhouse requires matching each device's capabilities to the environmental conditions (high humidity, water spray, and radio attenuation in `south-bed`) and computing demands (sensing versus local edge control).

| Hardware Platform | Role in Architecture | Key Strengths | Limitations in Greenhouse Context | Suitability for greenhouse-d |
| --- | --- | --- | --- | --- |
| Arduino (e.g., Uno / Nano / MKR WAN) | Basic sensor node or relay controller | Low cost, low power consumption, simple direct analog/digital interfacing for moisture probes and relays. | No operating system or local database storage for buffering; bare boards require custom waterproof enclosures and external radio modules. | Moderate (suitable only for simple low-cost sensing/actuation nodes if properly sealed, not suitable as a gateway). |
| Waspmote (Libelium Plug & Sense! Smart Agriculture) | Field sensor node in growing beds | Built for agriculture with IP65 weatherproof casing, solar battery charging, dedicated soil moisture/light/temperature ports, and long-range sub-GHz/LoRa radios. | Higher upfront cost per node than basic Arduino boards; not meant for running heavy Python analytics or local databases. | High for Sensing Tier (directly addresses `south-bed` weak RSSI of -82 dBm and protects probes against moisture-induced calibration drift). |
| Raspberry Pi (e.g., Pi 4 / Pi 5 or Industrial CM4) | Local edge/fog gateway | Runs full Linux, Python, local MQTT broker (Mosquitto), and local SQLite/InfluxDB store-and-forward buffering during network degradation. | Needs continuous power supply; standard consumer Pi boards and SD cards can fail in humid greenhouse air without an IP65 enclosure and SSD/eMMC storage. | High for Edge Gateway Tier (ideal for running local `edge_action_priority` rules and buffering data during the 191 ms latency spikes). |
| Industrial IoT Hardware (e.g., Siemens IOT2050 / Advantech PLC) | Rugged edge controller and actuator interface | Industrial temperature/humidity rating, DIN-rail mounting, hardware watchdog timers, and reliable 24V relay outputs for solenoid valves and fans. | Highest hardware cost and requires more specialised setup than consumer boards. | High for Actuation & Commercial Gateway (best option for reliably driving irrigation solenoids and fans to eliminate the 260 hours of `actuator_mismatch`). |

For `greenhouse-d`, the most practical combination is deploying Waspmote Smart Agriculture nodes in `north-bed` and `south-bed` for reliable wireless sensing, connected to an enclosed industrial Raspberry Pi CM4 (or industrial IoT gateway) that runs local edge control and buffers telemetry when the backhaul degrades.

## 7. Security, Privacy, And Risk Reflection

Because smart greenhouse systems connect digital networks directly to physical water valves and ventilation fans, security or data integrity failures can cause real physical damage to crops and waste limited water supplies.

1. Sensing and Actuation Domain Risks: Sensor nodes inside the greenhouse beds are exposed to moisture ingress, physical tampering, and sensor spoofing or calibration drift. In `greenhouse-d`, the 14 negative `light_lux` readings in `south-bed` while `sensor_status` reported `ok` and the 3-hour soil moisture dropout on 22 September show how easily faulty or manipulated sensor inputs could mislead an automated controller. If an attacker injected false high soil-moisture readings (or if drift went unchecked), the controller would keep irrigation off during severe drought, destroying the crop. Conversely, false low readings would leave valves open and drain the constrained water supply. To mitigate this, nodes should be housed in locked IP65 enclosures, use authenticated device identities, and be checked by edge plausibility rules that reject impossible values (such as `light_lux < 0`) and cross-check `irrigation_active` states against actual `water_flow_lpm` sensor readings.
2. Gateway and Network Domain Risks: The wireless link between `south-bed` and the gateway is already weak (`gateway_rssi_dbm` down to -82 dBm), and the gateway experiences a 7-hour `gateway_degraded` window with 191 ms latency and 4.54% packet loss. An attacker could exploit unencrypted wireless traffic to eavesdrop on telemetry, replay old actuator commands to turn off fans during a heat spike, or jam the weak radio signal in `south-bed`. To reduce these risks, sensor-to-gateway links should use link-layer encryption (such as AES-128) with message counters/timestamps to block replay attacks, while gateway-to-cloud traffic must use MQTT over TLS with mutual certificate authentication. Most importantly, keeping closed-loop irrigation and fan fallback logic on the local gateway ensures that network congestion or denial-of-service on the cloud link cannot stop critical greenhouse actuation during the 45 `edge_action_priority` hours.
3. Cloud and Platform Domain Risks: While greenhouse telemetry does not contain personal health data, commercial production records, water consumption rates, and crop stress histories are sensitive business data for the grower. Poorly secured cloud dashboards or shared passwords could allow unauthorised users to view operational data or remotely alter the `thresholds` dictionary (for example, raising the temperature limit or lowering the soil moisture trigger). This should be managed through role-based access control (RBAC), multi-factor authentication (MFA) for dashboard accounts, separate read-only versus control permissions, and audit logging of any threshold or manual actuator changes.

## 8. References

Barton, R., Hanes, D., Salgueiro, G., Grossetete, P., & Henry, J. (2017). IoT fundamentals: Networking technologies, protocols, and use cases for the Internet of Things. Cisco Press.

Lea, P. (2020). IoT and edge computing for architects: Implementing edge and IoT systems from sensors to clouds with communication systems, analytics, and security (2nd ed.). Packt Publishing.

Libelium. (2024). Waspmote Plug & Sense! Smart Agriculture PRO technical guide. Libelium Comunicaciones Distribuidas S.L.

National Institute of Standards and Technology. (2020). Foundational cybersecurity activities for IoT device manufacturers (NISTIR 8259). U.S. Department of Commerce. https://doi.org/10.6028/NIST.IR.8259

Tzounis, A., Katsoulas, N., Bartzanas, T., & Kittas, C. (2017). Internet of Things in agriculture, recent advances and future challenges. Biosystems Engineering, 164, 31-48. https://doi.org/10.1016/j.biosystemseng.2017.09.007

## 9. AI Use Declaration

Limited use of Generative AI is permitted for the coding component only. It must not be used to write your report, interpret the data for you, create recommendations, complete the security and privacy reflection, or replace your own professional judgement.

| Tool used | Coding purpose | Prompt(s) used | How I checked and revised the output |
| --- | --- | --- | --- |
| Google Gemini | Syntax cross-check for matplotlib subplot formatting and pandas group interpolation in the notebook. | "How do I plot a two-panel matplotlib chart by zone with horizontal threshold lines and scatter points for active irrigation?" | I cross-checked the plotting and pandas syntax against my existing notebook variables, ran the cells on my greenhouse-d dataset, and manually verified all counts and chart outputs against the CSV data. |
