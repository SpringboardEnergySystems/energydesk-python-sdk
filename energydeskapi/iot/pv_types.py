"""
Canonical metric key names and enum types for PV (solar) inverter telemetry.

Modelled on the Growatt MAX 50KTL3-XL three-phase string inverter as reported
by Grott v2.8.3 (proxy mode, protocol T065104XMAX, data-logger ShineLanBox).
The constants are device-agnostic strings suitable for use in
TelemetryEvent.points and for writing to NATS / InfluxDB.

InfluxDB storage convention
----------------------------
Use the constant's ``.value`` (str) as an InfluxDB field key, e.g.::

    measurement = "pv_inverter"
    fields: pvpowerin=5999.4, pvpowerout=5896.8, eactoday=72.3, ...
    tags:   pvserial="QRHED7N00K", pvstatus=1

The ``.name`` attribute is suitable for log lines and human-readable output.
"""
from __future__ import annotations

from enum import IntEnum


# ---------------------------------------------------------------------------
# Standard metric key names
# ---------------------------------------------------------------------------

class PvGrowattMetric:
    """
    Canonical string keys for Growatt solar inverter telemetry points.

    Use these constants as dict keys in ``TelemetryEvent.points`` so that all
    Growatt integrations emit the same field names regardless of the Grott
    layout version or firmware in use.

    Each constant's value is the literal string written to NATS / InfluxDB.
    Vendor-specific reader modules are responsible for mapping their raw
    register/JSON keys onto these names before publishing.

    Grouping
    --------
    Identification:
        SERIAL, STATUS

    DC input — total:
        DC_POWER_IN

    DC input — per MPPT tracker (1–8):
        PV{n}_VOLTAGE, PV{n}_CURRENT, PV{n}_WATT  (n = 1 … 8)
        Trackers 7 and 8 are not wired on the MAX 50KTL3-XL and will
        always report 0.0.

    AC output — total and per phase (L1–L3):
        AC_POWER_OUT, GRID_FREQUENCY,
        GRID_VOLTAGE_L{n}, GRID_CURRENT_L{n}, GRID_POWER_L{n}  (n = 1, 2, 3)

    AC output — apparent / reactive power:
        OUT_APPARENT_POWER, REACTIVE_POWER_REAL,
        REACTIVE_POWER_NOMINAL, REACTIVE_POWER_TOTAL

    Energy — cumulative AC / DC totals:
        AC_ENERGY_TODAY, AC_ENERGY_TOTAL, DC_ENERGY_TOTAL

    Energy — per MPPT tracker (1–8):
        EPV{n}_TODAY, EPV{n}_TOTAL  (n = 1 … 8)

    Energy — charge / auxiliary:
        CHARGE_ENERGY_TODAY, CHARGE_ENERGY_TOTAL

    Runtime:
        TOTAL_WORK_TIME

    Temperatures:
        TEMP_INVERTER, TEMP_IPM, TEMP_BOOST, TEMP_AMBIENT

    Fault / warning codes:
        FAULT_CODE, WARNING_CODE, FAULT_BITFIELD, WARNING_BITFIELD,
        FAULT_VALUE, PID_FAULT_CODE

    Grid / system safety measurements:
        ISO_FAULT_VALUE, GFCI_VALUE, DCI_ARC_VALUE

    Inverter / communication metadata:
        DATALOGGER_SERIAL, DEVICE_TYPE, FIRMWARE_VERSION,
        COMMUNICATION_VERSION
    """

    # ── Identification ─────────────────────────────────────────────────────
    SERIAL                   = "pvserial"                  # Inverter serial number (str)
    STATUS                   = "pvstatus"                  # Operating status (1 = normal)

    # ── DC input — total ───────────────────────────────────────────────────
    DC_POWER_IN              = "pvpowerin"                 # W  – total DC power from all strings

    # ── DC input — MPPT 1 ─────────────────────────────────────────────────
    PV1_VOLTAGE              = "pv1voltage"                # V  – DC voltage MPPT 1
    PV1_CURRENT              = "pv1current"                # A  – DC current MPPT 1
    PV1_WATT                 = "pv1watt"                   # W  – DC power  MPPT 1

    # ── DC input — MPPT 2 ─────────────────────────────────────────────────
    PV2_VOLTAGE              = "pv2voltage"                # V
    PV2_CURRENT              = "pv2current"                # A
    PV2_WATT                 = "pv2watt"                   # W

    # ── DC input — MPPT 3 ─────────────────────────────────────────────────
    PV3_VOLTAGE              = "pv3voltage"                # V
    PV3_CURRENT              = "pv3current"                # A
    PV3_WATT                 = "pv3watt"                   # W

    # ── DC input — MPPT 4 ─────────────────────────────────────────────────
    PV4_VOLTAGE              = "pv4voltage"                # V
    PV4_CURRENT              = "pv4current"                # A
    PV4_WATT                 = "pv4watt"                   # W

    # ── DC input — MPPT 5 ─────────────────────────────────────────────────
    PV5_VOLTAGE              = "pv5voltage"                # V
    PV5_CURRENT              = "pv5current"                # A
    PV5_WATT                 = "pv5watt"                   # W

    # ── DC input — MPPT 6 ─────────────────────────────────────────────────
    PV6_VOLTAGE              = "pv6voltage"                # V
    PV6_CURRENT              = "pv6current"                # A
    PV6_WATT                 = "pv6watt"                   # W

    # ── DC input — MPPT 7 (not connected on MAX 50KTL3-XL) ────────────────
    PV7_VOLTAGE              = "pv7voltage"                # V  – always 0.0
    PV7_CURRENT              = "pv7current"                # A  – always 0.0
    PV7_WATT                 = "pv7watt"                   # W  – always 0.0

    # ── DC input — MPPT 8 (not connected on MAX 50KTL3-XL) ────────────────
    PV8_VOLTAGE              = "pv8voltage"                # V  – always 0.0
    PV8_CURRENT              = "pv8current"                # A  – always 0.0
    PV8_WATT                 = "pv8watt"                   # W  – always 0.0

    # ── AC output — total ──────────────────────────────────────────────────
    AC_POWER_OUT             = "pvpowerout"                # W  – total AC power delivered to grid
    GRID_FREQUENCY           = "pvfrequentie"              # Hz – grid frequency

    # ── AC output — phase L1 ──────────────────────────────────────────────
    GRID_VOLTAGE_L1          = "pvgridvoltage"             # V  – AC voltage phase L1
    GRID_CURRENT_L1          = "pvgridcurrent"             # A  – AC current phase L1
    GRID_POWER_L1            = "pvgridpower"               # W  – AC power  phase L1

    # ── AC output — phase L2 ──────────────────────────────────────────────
    GRID_VOLTAGE_L2          = "pvgridvoltage2"            # V
    GRID_CURRENT_L2          = "pvgridcurrent2"            # A
    GRID_POWER_L2            = "pvgridpower2"              # W

    # ── AC output — phase L3 ──────────────────────────────────────────────
    GRID_VOLTAGE_L3          = "pvgridvoltage3"            # V
    GRID_CURRENT_L3          = "pvgridcurrent3"            # A
    GRID_POWER_L3            = "pvgridpower3"              # W

    # ── AC output — apparent / reactive power ─────────────────────────────
    OUT_APPARENT_POWER       = "out_apparent_pwr"          # VA  – total apparent power
    REACTIVE_POWER_REAL      = "reactive_pwr_real"         # VAr – reactive power, measured
    REACTIVE_POWER_NOMINAL   = "reactive_pwr_nominal"      # VAr – reactive power, nominal
    REACTIVE_POWER_TOTAL     = "reactive_pwr_tot"          # VAr – reactive power, total

    # ── Energy — cumulative AC / DC totals ────────────────────────────────
    AC_ENERGY_TODAY          = "eactoday"                  # kWh – AC energy produced today
    AC_ENERGY_TOTAL          = "eactotal"                  # kWh – AC energy produced lifetime
    DC_ENERGY_TOTAL          = "epvtotal"                  # kWh – DC energy input lifetime

    # ── Energy — MPPT 1 ───────────────────────────────────────────────────
    EPV1_TODAY               = "epv1today"                 # kWh – DC energy from MPPT 1 today
    EPV1_TOTAL               = "epv1total"                 # kWh – DC energy from MPPT 1 lifetime

    # ── Energy — MPPT 2 ───────────────────────────────────────────────────
    EPV2_TODAY               = "epv2today"                 # kWh
    EPV2_TOTAL               = "epv2total"                 # kWh

    # ── Energy — MPPT 3 ───────────────────────────────────────────────────
    EPV3_TODAY               = "epv3today"                 # kWh
    EPV3_TOTAL               = "epv3total"                 # kWh

    # ── Energy — MPPT 4 ───────────────────────────────────────────────────
    EPV4_TODAY               = "epv4today"                 # kWh
    EPV4_TOTAL               = "epv4total"                 # kWh

    # ── Energy — MPPT 5 ───────────────────────────────────────────────────
    EPV5_TODAY               = "epv5today"                 # kWh
    EPV5_TOTAL               = "epv5total"                 # kWh

    # ── Energy — MPPT 6 ───────────────────────────────────────────────────
    EPV6_TODAY               = "epv6today"                 # kWh
    EPV6_TOTAL               = "epv6total"                 # kWh

    # ── Energy — MPPT 7 / 8 (not connected) ───────────────────────────────
    EPV7_TODAY               = "epv7today"                 # kWh – always 0.0
    EPV8_TODAY               = "epv8today"                 # kWh – always 0.0

    # ── Energy — charge / auxiliary ───────────────────────────────────────
    CHARGE_ENERGY_TODAY      = "eacharge_today"            # kWh – charge energy today
    CHARGE_ENERGY_TOTAL      = "eacharge_total"            # kWh – charge energy lifetime

    # ── Runtime ───────────────────────────────────────────────────────────
    TOTAL_WORK_TIME          = "totworktime"               # s   – cumulative inverter run time

    # ── Temperatures ──────────────────────────────────────────────────────
    TEMP_INVERTER            = "pvtemperature"             # °C  – inverter / heatsink temperature
    TEMP_IPM                 = "pvipmtemperature"          # °C  – IPM (IGBT power module) temperature
    TEMP_BOOST               = "pvboosttemperature"        # °C  – boost section temperature
    TEMP_AMBIENT             = "temp4"                     # °C  – ambient temperature (if available)

    # ── Fault / warning codes ─────────────────────────────────────────────
    FAULT_CODE               = "pvfaultcode"               # int – primary fault code (0 = no fault)
    WARNING_CODE             = "pvwarncode"                # int – primary warning code
    FAULT_BITFIELD           = "faultbitcode"              # int – fault bitmask register
    WARNING_BITFIELD         = "warnbitcode"               # int – warning bitmask register
    FAULT_VALUE              = "faultvalue"                # float – measured value at fault point
    PID_FAULT_CODE           = "pidFaultCode"              # int – PID fault code

    # ── Grid / system safety measurements ────────────────────────────────
    ISO_FAULT_VALUE          = "isofaultvalue"             # kΩ  – insulation resistance at fault
    GFCI_VALUE               = "gfcifaultvalue"            # mA  – GFCI leakage current
    DCI_ARC_VALUE            = "dcifaultvalue"             # A   – DC injection / arc fault value

    # ── Inverter / communication metadata ────────────────────────────────
    DATALOGGER_SERIAL        = "logserial"                 # str – ShineLanBox / data-logger serial
    DEVICE_TYPE              = "pvdevicetype"              # str – device type string from logger
    FIRMWARE_VERSION         = "pvfirmwareversion"         # str – inverter main firmware version
    COMMUNICATION_VERSION    = "pvcommunicationversion"    # str – communication firmware version


# ---------------------------------------------------------------------------
# Inverter operating status
# ---------------------------------------------------------------------------

class PvInverterStatus(IntEnum):
    """
    Growatt ``pvstatus`` field values.

    Stored as an integer field in InfluxDB.  Use ``label`` for human-readable
    output or log messages.
    """
    STANDBY   = 0   # Waiting / standby (no sufficient irradiance)
    NORMAL    = 1   # Normal grid-connected operation
    FAULT     = 2   # Fault / error condition — check fault codes
    CHECKING  = 3   # Self-check / initialisation in progress
    OFF       = 5   # Powered off or communication lost

    @property
    def label(self) -> str:
        return _PV_STATUS_LABELS[self]


_PV_STATUS_LABELS: dict[PvInverterStatus, str] = {
    PvInverterStatus.STANDBY:  "Standby",
    PvInverterStatus.NORMAL:   "Normal",
    PvInverterStatus.FAULT:    "Fault",
    PvInverterStatus.CHECKING: "Checking",
    PvInverterStatus.OFF:      "Off",
}


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

#: Ordered tuple of active MPPT tracker indices for the MAX 50KTL3-XL.
#: Trackers 7 and 8 exist in the protocol but are not wired on this model.
ACTIVE_MPPT_INDICES: tuple[int, ...] = (1, 2, 3, 4, 5, 6)

#: All MPPT indices reported by Grott (including unwired ones).
ALL_MPPT_INDICES: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8)


def mppt_keys(tracker: int) -> dict[str, str]:
    """
    Return a dict mapping ``{"voltage": key, "current": key, "watt": key}``
    for the given MPPT tracker number (1–8).

    Example::

        keys = mppt_keys(3)
        # {"voltage": "pv3voltage", "current": "pv3current", "watt": "pv3watt"}
    """
    if tracker not in ALL_MPPT_INDICES:
        raise ValueError(f"tracker must be in {ALL_MPPT_INDICES}, got {tracker}")
    n = tracker
    return {
        "voltage": f"pv{n}voltage",
        "current": f"pv{n}current",
        "watt":    f"pv{n}watt",
    }


def growatt_status_to_pv_status(raw: int) -> PvInverterStatus:
    """
    Map a raw ``pvstatus`` integer from Grott to a :class:`PvInverterStatus`.

    Unknown values fall back to ``PvInverterStatus.STANDBY``.
    """
    try:
        return PvInverterStatus(raw)
    except ValueError:
        return PvInverterStatus.STANDBY

