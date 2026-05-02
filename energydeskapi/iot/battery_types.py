"""
Generic battery enum types for IoT telemetry and InfluxDB storage.

These types are device-agnostic and shared across battery integrations
(Victron VE.Bus, Ekoda ESS, etc.).  Vendor-specific codes are mapped to
these enums before being written to InfluxDB via the influx-sink.

InfluxDB storage convention
---------------------------
Store the `.value` (int) as a field or tag, e.g.:
    measurement="battery"
    fields: operation_mode=2, charge_stage=1, ac_input_status=1, ...

The `.name` (str) is suitable for log lines and human-readable output.
"""
from __future__ import annotations
from enum import IntEnum


# ---------------------------------------------------------------------------
# Top-level operating mode — "what is the battery system doing right now?"
# ---------------------------------------------------------------------------

class BatteryOperationMode(IntEnum):
    """
    Coarse operating mode, common across all battery / inverter-charger types.
    Suitable as an InfluxDB integer field or tag.
    """
    UNKNOWN        = 0
    OFF            = 1   # System is switched off
    CHARGING       = 2   # AC → Battery (any charge stage)
    INVERTING      = 3   # Battery → AC (no grid / off-grid output)
    PASSTHROUGH    = 4   # AC passes through; battery neither charged nor discharged
    FAULT          = 5   # Error / alarm condition
    STANDBY        = 6   # Low-power / idle (grid present, minimal draw)
    ESS            = 7   # Energy Storage System / grid-parallel optimisation

    @property
    def label(self) -> str:
        return _OPERATION_MODE_LABELS[self]


_OPERATION_MODE_LABELS: dict[BatteryOperationMode, str] = {
    BatteryOperationMode.UNKNOWN:     "Unknown",
    BatteryOperationMode.OFF:         "Off",
    BatteryOperationMode.CHARGING:    "Charging",
    BatteryOperationMode.INVERTING:   "Inverting",
    BatteryOperationMode.PASSTHROUGH: "Passthrough",
    BatteryOperationMode.FAULT:       "Fault",
    BatteryOperationMode.STANDBY:     "Standby",
    BatteryOperationMode.ESS:         "ESS / Grid-parallel",
}


# ---------------------------------------------------------------------------
# Charge stage — granular stage within a charge cycle
# ---------------------------------------------------------------------------

class BatteryChargeStage(IntEnum):
    """
    Detailed charge stage.  Only meaningful when BatteryOperationMode == CHARGING.
    Maps to standard multi-stage charger terminology.
    """
    NONE        = 0   # Not charging / not applicable
    BULK        = 1   # Constant-current phase (max charge current)
    ABSORPTION  = 2   # Constant-voltage phase (current tapering)
    FLOAT       = 3   # Maintenance float voltage
    STORAGE     = 4   # Long-term storage voltage (lower than float)
    EQUALIZE    = 5   # Periodic equalisation / balancing charge
    SUSTAIN     = 6   # Sustain mode (battery low, keep alive)

    @property
    def label(self) -> str:
        return _CHARGE_STAGE_LABELS[self]


_CHARGE_STAGE_LABELS: dict[BatteryChargeStage, str] = {
    BatteryChargeStage.NONE:       "None",
    BatteryChargeStage.BULK:       "Bulk",
    BatteryChargeStage.ABSORPTION: "Absorption",
    BatteryChargeStage.FLOAT:      "Float",
    BatteryChargeStage.STORAGE:    "Storage",
    BatteryChargeStage.EQUALIZE:   "Equalize",
    BatteryChargeStage.SUSTAIN:    "Sustain",
}


# ---------------------------------------------------------------------------
# AC input status
# ---------------------------------------------------------------------------

class AcInputStatus(IntEnum):
    DISCONNECTED = 0
    AC_INPUT_1   = 1
    AC_INPUT_2   = 2

    @property
    def label(self) -> str:
        return _AC_INPUT_LABELS[self]


_AC_INPUT_LABELS: dict[AcInputStatus, str] = {
    AcInputStatus.DISCONNECTED: "Disconnected",
    AcInputStatus.AC_INPUT_1:   "AC Input 1",
    AcInputStatus.AC_INPUT_2:   "AC Input 2",
}


# ---------------------------------------------------------------------------
# Victron VE.Bus → generic type mappers
# ---------------------------------------------------------------------------

# Raw VE.Bus state integer → (BatteryOperationMode, BatteryChargeStage)
_VEBUS_STATE_MAP: dict[int, tuple[BatteryOperationMode, BatteryChargeStage]] = {
    0:   (BatteryOperationMode.OFF,         BatteryChargeStage.NONE),
    1:   (BatteryOperationMode.STANDBY,     BatteryChargeStage.NONE),   # Low Power
    2:   (BatteryOperationMode.FAULT,       BatteryChargeStage.NONE),
    3:   (BatteryOperationMode.CHARGING,    BatteryChargeStage.BULK),
    4:   (BatteryOperationMode.CHARGING,    BatteryChargeStage.ABSORPTION),
    5:   (BatteryOperationMode.CHARGING,    BatteryChargeStage.FLOAT),
    6:   (BatteryOperationMode.CHARGING,    BatteryChargeStage.STORAGE),
    7:   (BatteryOperationMode.CHARGING,    BatteryChargeStage.EQUALIZE),
    8:   (BatteryOperationMode.PASSTHROUGH, BatteryChargeStage.NONE),
    9:   (BatteryOperationMode.INVERTING,   BatteryChargeStage.NONE),
    10:  (BatteryOperationMode.INVERTING,   BatteryChargeStage.NONE),   # Power assist
    11:  (BatteryOperationMode.CHARGING,    BatteryChargeStage.NONE),   # Power supply
    244: (BatteryOperationMode.CHARGING,    BatteryChargeStage.SUSTAIN),
    252: (BatteryOperationMode.ESS,         BatteryChargeStage.NONE),   # External control
}

# Victron active_input register values → AcInputStatus
_VEBUS_ACTIVE_INPUT_MAP: dict[int, AcInputStatus] = {
    0:   AcInputStatus.AC_INPUT_1,
    1:   AcInputStatus.AC_INPUT_2,
    240: AcInputStatus.DISCONNECTED,
}


def vebus_state_to_operation_mode(vebus_state: int) -> BatteryOperationMode:
    """Map a raw VE.Bus state integer to the generic BatteryOperationMode."""
    return _VEBUS_STATE_MAP.get(vebus_state, (BatteryOperationMode.UNKNOWN, BatteryChargeStage.NONE))[0]


def vebus_state_to_charge_stage(vebus_state: int) -> BatteryChargeStage:
    """Map a raw VE.Bus state integer to the generic BatteryChargeStage."""
    return _VEBUS_STATE_MAP.get(vebus_state, (BatteryOperationMode.UNKNOWN, BatteryChargeStage.NONE))[1]


def vebus_active_input_to_ac_status(active_input: int) -> AcInputStatus:
    """Map a raw VE.Bus active_input register value to AcInputStatus."""
    return _VEBUS_ACTIVE_INPUT_MAP.get(active_input, AcInputStatus.DISCONNECTED)

