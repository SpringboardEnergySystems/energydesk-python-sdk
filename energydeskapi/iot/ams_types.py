"""
Canonical metric key names for AMS smart-meter (HAN port) telemetry.

Modelled on the Aidon / Pow-U meter family (Norwegian HAN standard).
The constants are device-agnostic strings suitable for use in
TelemetryEvent.points and for writing to NATS / InfluxDB.

InfluxDB storage convention
----------------------------
Use the constant's value (str) as an InfluxDB field key, e.g.::

    measurement = "ams_meter"
    fields: active_power=558.0, reactive_power=0.0,
            voltage_l1=236.0, current_l1=1.1, ...
    tags:   meter_id="7359992900679092", site="NO1"
"""
from __future__ import annotations


class AmsMainMeterMetric:
    """
    Canonical string keys for AMS main meter (grid import/export) telemetry.

    Use these constants as dict keys in ``TelemetryEvent.points`` so that all
    AMS integrations (Aidon, Kamstrup, …) emit the same field names regardless
    of the underlying meter brand or HAN-port reader.

    Each constant's value is the literal string written to NATS / InfluxDB.
    Vendor-specific parser modules are responsible for mapping their raw
    field names onto these names before publishing.

    Grouping
    --------
    Active power:
        ACTIVE_POWER, ACTIVE_POWER_EXPORT

    Reactive power:
        REACTIVE_POWER, REACTIVE_POWER_EXPORT

    Per-phase current (L1–L3):
        CURRENT_L1, CURRENT_L2, CURRENT_L3

    Per-phase voltage (L1–L3):
        VOLTAGE_L1, VOLTAGE_L2, VOLTAGE_L3
    """

    # ── Active power ──────────────────────────────────────────────────────────
    ACTIVE_POWER          = "active_power"          # W   – instantaneous active import power
    ACTIVE_POWER_EXPORT   = "active_power_export"   # W   – instantaneous active export power

    # ── Reactive power ────────────────────────────────────────────────────────
    REACTIVE_POWER        = "reactive_power"        # VAr – reactive import power
    REACTIVE_POWER_EXPORT = "reactive_power_export" # VAr – reactive export power

    # ── Per-phase current ─────────────────────────────────────────────────────
    CURRENT_L1            = "current_l1"            # A   – phase 1 current
    CURRENT_L2            = "current_l2"            # A   – phase 2 current
    CURRENT_L3            = "current_l3"            # A   – phase 3 current

    # ── Per-phase voltage ─────────────────────────────────────────────────────
    VOLTAGE_L1            = "voltage_l1"            # V   – phase 1 voltage
    VOLTAGE_L2            = "voltage_l2"            # V   – phase 2 voltage
    VOLTAGE_L3            = "voltage_l3"            # V   – phase 3 voltage

