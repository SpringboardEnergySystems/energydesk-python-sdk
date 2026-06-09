"""
energydeskapi/iot/schemas.py

NATS message schemas shared across all workers and the VEN server.
These are the canonical definitions — no other repo should define its own
versions of Command, ResultEvent, TelemetryEvent, or HeartbeatEvent.

Import from here in all workers:
    from energydeskapi.iot.schemas import Command, CommandType, ResultEvent, ResultStatus, ...
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Command types
# ---------------------------------------------------------------------------

class CommandType(str, Enum):
    """
    All supported command types across the worker fleet.

    Universal (all worker types):
        READ    — on-demand telemetry read outside the normal poll cycle
        TUNE    — adjust runtime config (e.g. poll interval) without restart

    Battery / ESS — goal-based (dispatcher owns closed-loop tracking):
        SETPOINT_SOC    — charge/discharge to a target State of Charge (%)
                          payload: target_soc, ramp_rate_kw (optional),
                                   soc_tolerance (optional, default 2.0),
                                   valid_until (optional)
        SETPOINT_POWER  — direct power command in kW (positive=charge,
                          negative=discharge). Used internally by dispatcher
                          when translating SOC targets into device commands.
                          payload: p_kw, valid_until (optional)
        SETPOINT_CANCEL — cancel the active setpoint; worker should idle
                          payload: setpoint_id (optional, for confirmation)

    Mode-based devices (e.g. Victron MultiPlus without ESS assistant):
        SET_SWITCH      — set inverter/charger mode
                          payload: position (1=ChargerOnly 2=InverterOnly
                                             3=On 4=Off)
        SET_CURRENT     — set AC input current limit
                          payload: amps (float)

    Note: SETPOINT_SOC and SETPOINT_POWER should be rejected (ResultStatus.REJECTED)
    by workers whose hardware does not support fine-grained power control.
    Workers advertise their supported command types via self-registration.
    """
    # Universal
    READ            = "read"
    TUNE            = "tune"
    # Battery / ESS
    SETPOINT_SOC    = "setpoint_soc"
    SETPOINT_POWER  = "setpoint_power"
    SETPOINT_CANCEL = "setpoint_cancel"
    # Mode-based
    SET_SWITCH      = "set_switch"
    SET_CURRENT     = "set_current"


# ---------------------------------------------------------------------------
# Result status
# ---------------------------------------------------------------------------

class ResultStatus(str, Enum):
    """
    Status values for ResultEvent.

    OK           — command fully executed (e.g. Modbus write confirmed).
                   For setpoints this means the write was accepted by the
                   device, not that the goal (SOC target) has been reached.
    ACKNOWLEDGED — command received and schema-validated; execution is
                   in progress (useful for async / long-running setpoints).
    DONE         — goal reached (e.g. SOC within tolerance of target).
                   Only used for SETPOINT_SOC; other commands use OK.
    ERROR        — execution failed (Modbus error, timeout, unexpected exception).
    TIMEOUT      — deadline_ms exceeded before the device responded.
    REJECTED     — command was understood but refused by the worker.
                   Reasons include: unsupported command type for this device,
                   value out of hardware-safe range, device in local control
                   mode, setpoint_id not found. The error field will contain
                   a human-readable explanation.
                   Unlike ERROR, REJECTED means the device was not touched.
    """
    OK           = "ok"
    ACKNOWLEDGED = "acknowledged"
    DONE         = "done"
    ERROR        = "error"
    TIMEOUT      = "timeout"
    REJECTED     = "rejected"


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseModel):
    """
    Issued by the regulation dispatcher (or VEN server) to a worker.

    Routing: published on NATS subject cmd.<worker_type>.<site>.<device>
    e.g. cmd.ekoda.fana.battery-01

    setpoint_id links the command back to the device_setpoints DB row so
    the dispatcher can correlate ResultEvents with the originating setpoint.
    valid_until allows the worker to self-expire a setpoint if the dispatcher
    goes silent (defence in depth — the dispatcher also tracks expiry).
    """
    command_id:  str          = Field(default_factory=lambda: str(uuid.uuid4()))
    type:        CommandType
    site:        str
    device:      str
    payload:     Dict[str, Any] = Field(default_factory=dict)
    issued_at:   datetime     = Field(default_factory=utcnow)
    deadline_ms: int          = 5000
    # Setpoint lifecycle — present for SETPOINT_* commands, None otherwise
    setpoint_id: Optional[int]      = None
    valid_until: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Result event
# ---------------------------------------------------------------------------

class ResultEvent(BaseModel):
    """
    Published by a worker in response to a Command.

    Routing: published on NATS subject evt.<worker_type>.result.<site>.<device>
    e.g. evt.ekoda.result.fana.battery-01

    A single Command may produce multiple ResultEvents over its lifetime:
      1. ACKNOWLEDGED — immediately on receipt (schema valid, device will be contacted)
      2. OK           — Modbus write confirmed (for SETPOINT_SOC / SETPOINT_POWER)
      3. DONE         — SOC target reached ± tolerance (SETPOINT_SOC only)

    For simple commands (READ, TUNE, SET_SWITCH, SET_CURRENT) a single OK
    or ERROR/TIMEOUT/REJECTED is sufficient.

    current_soc is included where available so the dispatcher can update its
    view of the device state without waiting for the next TelemetryEvent.
    """
    command_id:  str
    setpoint_id: Optional[int]   = None   # echoed from Command for correlation
    site:        str
    device:      str
    worker_id:   str
    status:      ResultStatus
    duration_ms: int
    error:       Optional[str]   = None
    data:        Dict[str, Any]  = Field(default_factory=dict)
    current_soc: Optional[float] = None   # % — included when available
    ts:          datetime        = Field(default_factory=utcnow)


# ---------------------------------------------------------------------------
# Telemetry event
# ---------------------------------------------------------------------------

class TelemetryEvent(BaseModel):
    """
    Published by a worker on its autonomous poll loop and on READ commands.

    Routing: published on NATS subject evt.<worker_type>.telemetry.<site>.<device>
    e.g. evt.ekoda.telemetry.fana.battery-01

    points keys should use BatteryMetric / PvMetric constants from
    energydeskapi.iot.battery_types / pv_types — never raw vendor register names.
    resource_type is the ResourceType string value used as the InfluxDB
    measurement name by the influx-sink.
    """
    site:          str
    device:        str
    worker_id:     str
    points:        Dict[str, float]
    resource_type: Optional[str] = None
    ts:            datetime      = Field(default_factory=utcnow)


# ---------------------------------------------------------------------------
# Heartbeat event
# ---------------------------------------------------------------------------

class HeartbeatEvent(BaseModel):
    """
    Published by a worker once per minute.

    Routing: published on NATS subject evt.<worker_type>.heartbeat.<site>.<worker_id>
    e.g. evt.ekoda.heartbeat.fana.ekoda-rpi-fana

    device_id matches FlexibleResource.resource_external_id in the VEN server DB
    so the portal can update last_heartbeat_at for the registered resource.
    capabilities lists the CommandType values this worker accepts — used by
    the regulation dispatcher to know what commands are safe to issue.
    """
    site:               str
    worker_id:          str
    device_id:          Optional[str]        = None
    status:             ResultStatus         = ResultStatus.OK
    connected_devices:  int                  = 0
    last_io_ts:         Optional[datetime]   = None
    capabilities:       List[CommandType]    = Field(default_factory=list)
    version:            str                  = "0.1.0"
    ts:                 datetime             = Field(default_factory=utcnow)


# ---------------------------------------------------------------------------
# Self-registration payload
# ---------------------------------------------------------------------------

class WorkerRegistration(BaseModel):
    """
    Posted by a worker to POST /api/resources/self-register on the VEN server.

    capabilities declares which CommandType values the worker accepts.
    The VEN server stores this so the portal and dispatcher know what each
    device can do without inspecting worker code.

    setpoint_type summarises the control model:
        "soc"   — accepts SETPOINT_SOC (goal-based, dispatcher tracks completion)
        "power" — accepts SETPOINT_POWER (direct kW, dispatcher tracks completion)
        "mode"  — accepts SET_SWITCH / SET_CURRENT only (mode-based, no SOC target)
        "none"  — read-only worker (telemetry only, no write commands)
    """
    resource_external_id: str
    resource_type:        str
    worker_id:            str
    nats_cmd_prefix:      str
    nats_evt_prefix:      str
    capabilities:         List[CommandType] = Field(default_factory=list)
    setpoint_type:        str               = "none"   # soc | power | mode | none
    description:          Optional[str]     = None