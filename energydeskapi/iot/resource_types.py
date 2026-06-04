"""
Authoritative device/resource type taxonomy for the Energydesk IoT platform.

This is the single source of truth used by:
  - IoT workers  (set TelemetryEvent.resource_type before publishing)
  - influx-sink  (resolves InfluxDB measurement name from resource_type)
  - venserver    (FlexibleResource / PendingResource DB columns)
  - portal       (registration UI, Flux queries)

InfluxDB measurement naming rule
---------------------------------
The ResourceType string value IS the InfluxDB measurement name — no lookup
table needed::

    measurement = tel.resource_type   # e.g. "battery", "solar", "main_meter"

Worker taxonomy
---------------
Dedicated workers (one repo per type):

    BATTERY     energydesk-rpi-ekodabattery  /  future Victron worker
    SOLAR       energydesk-rpi-growattpv
    MAIN_METER  energydesk-rpi-amsreader

Generic asset worker (one pod per site, N assets via DEVICES_JSON):

    EV_CHARGER, HEAT_PUMP, HVAC, LOAD, WIND, GENERATOR, OTHER
    → energydesk-rpi-venclient / workers/asset-worker
"""
from __future__ import annotations
from enum import Enum


class ResourceType(str, Enum):
    """
    Physical device / resource type.

    Values are lowercase strings that double as InfluxDB measurement names
    and as the ``resource_type`` field in self-registration payloads and
    ``TelemetryEvent``.

    Adding a new type here is the only change needed to support a new
    device category end-to-end (SDK → worker → sink → Flux queries).
    """

    # ── Dedicated-worker types ────────────────────────────────────────────
    BATTERY     = "battery"      # Battery storage systems (Ekoda ESS, Victron)
    SOLAR       = "solar"        # PV solar inverters (Growatt)
    MAIN_METER  = "main_meter"   # Smart meter / AMS HAN-port reader

    # ── Asset-worker types (generic configurable worker) ──────────────────
    EV_CHARGER  = "ev_charger"   # EV charging station
    HEAT_PUMP   = "heat_pump"    # Heat pump system
    HVAC        = "hvac"         # HVAC / ventilation
    WIND        = "wind"         # Wind turbine
    GENERATOR   = "generator"    # Diesel / gas generator
    LOAD        = "load"         # Generic controllable load
    OTHER       = "other"        # Fallback for unclassified assets


def influx_measurement(resource_type: "str | ResourceType") -> str:
    """
    Return the InfluxDB measurement name for a given resource type.

    The rule is trivially simple: the ResourceType value IS the measurement
    name.  This function exists so call-sites are explicit and searchable,
    and provides a safe fallback for unknown strings.

    Examples::

        influx_measurement(ResourceType.BATTERY)   # → "battery"
        influx_measurement("solar")                # → "solar"
        influx_measurement("unknown_thing")        # → "other"
    """
    if isinstance(resource_type, ResourceType):
        return resource_type.value
    try:
        return ResourceType(resource_type).value
    except ValueError:
        return ResourceType.OTHER.value

