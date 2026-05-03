"""
Generic battery metric names and enum types for IoT telemetry and InfluxDB storage.

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
# Standard metric key names
# ---------------------------------------------------------------------------

class BatteryMetric:
    """
    Canonical string keys for battery telemetry points.

    Use these constants as dict keys in TelemetryEvent.points so that all
    battery integrations (Victron, Ekoda, …) emit the same field names
    regardless of the vendor's own naming conventions.

    Each constant's value is the literal string written to NATS / InfluxDB.
    Vendor-specific reader modules are responsible for mapping their raw
    register keys onto these names before publishing.

    Grouping
    --------
    Core battery:
        STATE_OF_CHARGE, BATTERY_VOLTAGE, BATTERY_CURRENT, BATTERY_POWER,
        DEVICE_STATE, DEVICE_ERROR, SWITCH_POSITION, PHASE_COUNT,
        ACTIVE_INPUT, OPERATION_MODE, CHARGE_STAGE, AC_INPUT_STATUS

    AC inverter-side (Victron VE.Bus style — input=grid side, output=load side):
        INPUT_VOLTAGE_L1, INPUT_CURRENT_L1, INPUT_FREQUENCY_L1, INPUT_POWER_L1,
        OUTPUT_VOLTAGE_L1, OUTPUT_CURRENT_L1, OUTPUT_FREQUENCY, OUTPUT_POWER_L1

    Grid / ESS (Ekoda ESS style — grid seen as a single AC bus):
        GRID_VOLTAGE, GRID_FREQUENCY, GRID_ACTIVE_POWER, GRID_CURRENT,
        AVAILABLE_CHARGE_POWER, AVAILABLE_DISCHARGE_POWER, AVAILABLE_ENERGY

    Ekoda ESS status bits (float 0.0 / 1.0):
        ESS_STATUS_WORD, ESS_FAULT, ESS_RUNNING, ESS_STARTING,
        ESS_STOPPING, ESS_LOCAL_REMOTE
    """

    # ── Core battery ───────────────────────────────────────────────────────
    STATE_OF_CHARGE          = "state_of_charge"           # %
    BATTERY_VOLTAGE          = "battery_voltage"           # V DC
    BATTERY_CURRENT          = "battery_current"           # A DC
    BATTERY_POWER            = "battery_power"             # W  (derived: V * A)
    DEVICE_STATE             = "device_state"              # raw vendor state int
    DEVICE_ERROR             = "device_error"              # raw vendor error code
    SWITCH_POSITION          = "switch_position"           # raw vendor int
    PHASE_COUNT              = "phase_count"               # int
    ACTIVE_INPUT             = "active_input"              # raw vendor int
    OPERATION_MODE           = "operation_mode"            # BatteryOperationMode.value
    CHARGE_STAGE             = "charge_stage"              # BatteryChargeStage.value
    AC_INPUT_STATUS          = "ac_input_status"           # AcInputStatus.value

    # ── AC inverter-side (Victron VE.Bus) ──────────────────────────────────
    INPUT_VOLTAGE_L1         = "input_voltage_l1"          # V AC
    INPUT_CURRENT_L1         = "input_current_l1"          # A AC
    INPUT_FREQUENCY_L1       = "input_frequency_l1"        # Hz
    INPUT_POWER_L1           = "input_power_l1"            # W
    OUTPUT_VOLTAGE_L1        = "output_voltage_l1"         # V AC
    OUTPUT_CURRENT_L1        = "output_current_l1"         # A AC
    OUTPUT_FREQUENCY         = "output_frequency"          # Hz
    OUTPUT_POWER_L1          = "output_power_l1"           # W

    # ── Grid / ESS (Ekoda) ─────────────────────────────────────────────────
    GRID_VOLTAGE             = "grid_voltage"              # V
    GRID_FREQUENCY           = "grid_frequency"            # Hz
    GRID_ACTIVE_POWER        = "grid_active_power"         # kW (negative = export)
    GRID_CURRENT             = "grid_current"              # A
    AVAILABLE_CHARGE_POWER   = "available_charge_power"    # kW
    AVAILABLE_DISCHARGE_POWER= "available_discharge_power" # kW
    AVAILABLE_ENERGY         = "available_energy"          # kWh

    # ── Ekoda ESS status bits ──────────────────────────────────────────────
    ESS_STATUS_WORD          = "ess_status_word"           # raw uint16 bitmask
    ESS_FAULT                = "ess_fault"                 # 0.0 / 1.0
    ESS_RUNNING              = "ess_running"               # 0.0 / 1.0
    ESS_STARTING             = "ess_starting"              # 0.0 / 1.0
    ESS_STOPPING             = "ess_stopping"              # 0.0 / 1.0
    ESS_LOCAL_REMOTE         = "ess_local_remote"          # 0.0=Local 1.0=Remote


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

