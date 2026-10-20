"""
Generic (device-independent) telemetry metrics.

Every device type publishes its own raw metrics (``BatteryMetric``,
``PvGrowattMetric``, ``AmsMainMeterMetric``, ...). Consumers that only need
"how much power is this asset drawing right now" — e.g. the VEN client
reporting meter values to the VTN — should not have to know which raw metric
that is for each device type.

The influx-sink therefore stores the raw points as published *and* a derived
generic point, in the same measurement with the same tags, using
:func:`derive_generic_points`.

Sign convention (load convention, matches the AMS main meter and the Victron
``grid_active_power``):

    positive = consumption / import from the grid
    negative = generation / export to the grid
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union

from energydeskapi.iot.ams_types import AmsMainMeterMetric
from energydeskapi.iot.battery_types import BatteryMetric
from energydeskapi.iot.pv_types import PvGrowattMetric
from energydeskapi.iot.resource_types import ResourceType


class GenericMetric:
    """Canonical device-independent metric keys."""

    ACTIVE_POWER_KW = "active_power_kw"   # kW, + = consumption/import, - = generation/export


# (raw metric key, multiplier to kW in load convention), tried in order.
_Source = Tuple[str, float]

_GRID_ACTIVE_POWER: List[_Source] = [(BatteryMetric.GRID_ACTIVE_POWER, 1.0)]

ACTIVE_POWER_SOURCES: Dict[str, List[_Source]] = {
    ResourceType.MAIN_METER.value: [
        (AmsMainMeterMetric.ACTIVE_POWER_KW, 1.0),
        (AmsMainMeterMetric.ACTIVE_POWER, 0.001),
    ],
    ResourceType.BATTERY.value: [
        (BatteryMetric.GRID_ACTIVE_POWER, 1.0),
        (BatteryMetric.BATTERY_POWER_KW, -1.0),   # + = discharge, so invert
    ],
    ResourceType.SOLAR.value: [
        (PvGrowattMetric.SOLAR_KW, -1.0),         # non-negative generation -> negative
        (PvGrowattMetric.AC_POWER_OUT, -0.001),   # W
        (BatteryMetric.GRID_ACTIVE_POWER, 1.0),   # already kW, negative = export
    ],
    ResourceType.EV_CHARGER.value: _GRID_ACTIVE_POWER,
    ResourceType.HEAT_PUMP.value: _GRID_ACTIVE_POWER,
    ResourceType.HVAC.value: _GRID_ACTIVE_POWER,
    ResourceType.LOAD.value: _GRID_ACTIVE_POWER,
}


def derive_generic_points(
    resource_type: Optional[Union[str, ResourceType]],
    points: Dict[str, float],
) -> Dict[str, float]:
    """
    Return the generic points derivable from raw ``points``.

    Returns ``{}`` when the resource type has no known source, none of its
    source metrics are present, or the generic metric was already published
    by the device itself (the device's own value wins).
    """
    key = resource_type.value if isinstance(resource_type, ResourceType) else resource_type
    if GenericMetric.ACTIVE_POWER_KW in points:
        return {}
    for metric, scale in ACTIVE_POWER_SOURCES.get(key or "", []):
        raw = points.get(metric)
        if raw is None:
            continue
        try:
            value = float(raw) * scale
        except (TypeError, ValueError):
            continue
        return {GenericMetric.ACTIVE_POWER_KW: value + 0.0}   # + 0.0 normalises -0.0
    return {}
