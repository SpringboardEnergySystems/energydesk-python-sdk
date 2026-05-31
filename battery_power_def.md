# Active Power Metric Definitions

Cross-device reference for all "active power" metrics used across the
Energydesk IoT stack.  Each section covers one device family, including the
canonical field name, its sign convention, unit, physical measurement point,
and how it relates to the metrics from the other devices.

---

## 1. Ekoda ESS Battery — `grid_active_power`

| Property | Value |
|---|---|
| **Canonical key** | `grid_active_power` (`BatteryMetric.GRID_ACTIVE_POWER`) |
| **Source** | Modbus holding register 7 — signed int16, raw value ÷ 10 → kW |
| **Unit** | kW |
| **Sign convention** | **Positive = importing from grid** (grid is charging the system); **Negative = exporting to grid** (system is discharging into grid) |
| **Measurement point** | AC bus at the utility connection — the boundary between the ESS inverter and the grid |
| **Role** | Primary control signal. Used by `ekoda_status_to_operation_mode()` with a ±0.05 kW dead band to classify the system as `CHARGING`, `INVERTING`, or `ESS`. |

---

## 2. Ekoda ESS Battery — `battery_power`

| Property | Value |
|---|---|
| **Canonical key** | `battery_power` (`BatteryMetric.BATTERY_POWER`) |
| **Source** | **Derived** — not a direct register. Computed as `battery_voltage × battery_current ÷ 1000` (kW). `battery_current` comes from register 11 (signed int16, ÷ 10 → A). |
| **Unit** | kW (note: the `BatteryMetric` docstring says "W" but the Ekoda reader divides by 1000 to produce kW) |
| **Sign convention** | **Positive = discharging** (current flows out of battery cells); **Negative = charging** (current flows in) |
| **Measurement point** | DC bus between battery pack and inverter |
| **Role** | Reflects actual energy movement at the cell level, independent of inverter conversion losses. |

### Relationship between `grid_active_power` and `battery_power`

They measure the same energy flow at **different boundaries** of the inverter:

```
  [Battery DC] ──► [Inverter] ──► [Grid AC]
       ↑                                ↑
  battery_power                 grid_active_power
  (DC boundary)                  (AC boundary)

  Difference = inverter conversion losses (typically 2–5 %)
```

They can have **opposite signs** — for example, when the system is in ESS
grid-parallel optimisation mode the grid exchange may be near zero while the
battery is actively cycling to absorb or supply local loads.

The Victron VE.Bus integration does **not** have a `grid_active_power`
register. Its AC side is instead split into `input_power_l1` (grid → inverter)
and `output_power_l1` (inverter → loads), which together are the Victron
equivalent. There is also no direct battery DC power register — `battery_power`
would need to be derived the same way (V × A) if added.

---

## 3. AMS Smart Meter — `active_power` and `active_power_export`

Defined in `energydeskapi.iot.ams_types.AmsMainMeterMetric`.
Sourced from the HAN port of the Norwegian AMS smart meter (Aidon / Pow-U
family), mapped in `worker/parsers/aidon.py`.

| Property | `active_power` | `active_power_export` |
|---|---|---|
| **Canonical key** | `active_power` | `active_power_export` |
| **Aidon raw field** | `P` | `PO` |
| **Unit** | W | W |
| **Sign convention** | Always **positive** — instantaneous watts being **imported** from the grid to the premises | Always **positive** — instantaneous watts being **exported** from the premises to the grid |
| **Measurement point** | The utility metering point — the legal boundary between the grid operator's network and the customer installation |
| **Typical non-zero condition** | Any load is consuming power | Solar or battery is exporting more than local loads consume |

> **Important:** The AMS meter uses **two separate positive fields** (import and
> export) rather than a single signed value. At any instant, one of them will
> be non-zero and the other will be zero (or a small leakage value).

### Relationship to battery metrics

The AMS meter sits at the **premises boundary**, one step further out than the
Ekoda `grid_active_power` which sits at the ESS inverter's AC terminal. In a
site with a battery and solar, the AMS reading is the **net** result visible to
the grid operator:

```
  [Battery]  [Solar]  [Loads]
       └──────┴──────┘
              │
        [Site internal AC bus]
              │
        [ESS inverter AC port]  ← grid_active_power (Ekoda, kW, signed)
              │
        [Distribution panel]
              │
     [AMS metering point]       ← active_power / active_power_export (W, two positive fields)
              │
          [Grid]
```

Mapping between sign conventions:

| Ekoda `grid_active_power` | AMS fields |
|---|---|
| Positive (importing) | `active_power` > 0, `active_power_export` = 0 |
| Negative (exporting) | `active_power` = 0, `active_power_export` > 0 |
| Near zero (ESS idle) | Both near 0 |

**Unit difference:** AMS reports in **W**; Ekoda `grid_active_power` is in **kW**.
Divide `active_power` / `active_power_export` by 1000 to compare directly.

---

## 4. Growatt Solar Inverter — `pvpowerin`, `pvpowerout`, and per-MPPT `pv{n}watt`

Defined in `energydeskapi.iot.pv_types.PvGrowattMetric`.
Reported by the Grott proxy (protocol T065104XMAX, ShineLanBox data-logger),
bridged via MQTT → NATS in `energydesk-rpi-growattpv`.

### 4.1 `pvpowerin` — total DC input power

| Property | Value |
|---|---|
| **Canonical key** | `pvpowerin` (`PvGrowattMetric.DC_POWER_IN`) |
| **Unit** | W |
| **Sign** | Always **positive** (solar panels only produce, never consume) |
| **Measurement point** | DC side of the inverter — sum of all MPPT tracker inputs |
| **Description** | Total solar DC power harvested from all PV strings before conversion losses. This is the "raw" solar generation figure. |

### 4.2 `pvpowerout` — total AC output power

| Property | Value |
|---|---|
| **Canonical key** | `pvpowerout` (`PvGrowattMetric.AC_POWER_OUT`) |
| **Unit** | W |
| **Sign** | Always **positive** |
| **Measurement point** | AC output terminals of the inverter — power delivered to the site AC bus (and ultimately the grid) |
| **Description** | Total AC power after inverter conversion. `pvpowerout` ≤ `pvpowerin`; the difference is inverter losses (heat). |

### 4.3 Per-MPPT DC power — `pv{n}watt` (n = 1 … 8)

| Property | Value |
|---|---|
| **Canonical keys** | `pv1watt` … `pv6watt` (active); `pv7watt`, `pv8watt` (always 0.0 — not wired on MAX 50KTL3-XL) |
| **Unit** | W |
| **Sign** | Always **positive** |
| **Measurement point** | Each individual MPPT tracker input |
| **Description** | DC power from a single string / MPPT tracker. `pv1watt + pv2watt + … + pv6watt ≈ pvpowerin` (small discrepancies from rounding are expected). |

Companion per-tracker fields: `pv{n}voltage` (V) and `pv{n}current` (A), where
`pv{n}watt ≈ pv{n}voltage × pv{n}current`.

### 4.4 Per-phase AC output — `pvgridpower`, `pvgridpower2`, `pvgridpower3`

| Property | Value |
|---|---|
| **Canonical keys** | `pvgridpower` (L1), `pvgridpower2` (L2), `pvgridpower3` (L3) |
| **Unit** | W |
| **Description** | AC power per phase on the output side. Sum ≈ `pvpowerout`. |

### Relationship to battery and AMS metrics

```
  [PV strings]
  pv1watt…pv6watt (per MPPT, W)
        │
  pvpowerin  (total DC, W)
        │
  [Growatt inverter]
        │ (conversion loss)
  pvpowerout (total AC, W)
        │
  [Site internal AC bus]  ◄── battery_power also feeds here (via Ekoda inverter)
        │
  [AMS metering point]
        │  net = loads + battery ± solar
  active_power / active_power_export (W)
        │
    [Grid]
```

| Growatt field | Corresponds to… |
|---|---|
| `pvpowerin` | Total DC harvest — compare with `battery_power` (kW × 1000) to see whether solar or battery is the dominant source |
| `pvpowerout` | Solar's contribution to the site AC bus — subtract from `active_power_export` to estimate how much of the export is purely solar |
| `pvpowerout` vs `grid_active_power` | Both sit on or near the AC bus but are measured by different devices; they are **not** subtracted — they are separate inputs to the site energy balance |

**Unit alignment note:** All Growatt watt fields are in **W**; Ekoda
`grid_active_power` and `battery_power` are in **kW**. Multiply the Ekoda
values by 1000 before combining them in energy-balance calculations.

---

## 5. Quick comparison table

| Field | Device | Key | Unit | Sign: positive means… | Measurement point |
|---|---|---|---|---|---|
| `grid_active_power` | Ekoda ESS | `BatteryMetric.GRID_ACTIVE_POWER` | kW | Importing from grid | ESS inverter AC terminal |
| `battery_power` | Ekoda ESS | `BatteryMetric.BATTERY_POWER` | kW | Discharging (to loads/grid) | Battery DC terminal |
| `active_power` | AMS meter | `AmsMainMeterMetric.ACTIVE_POWER` | W | Site importing from grid | Utility metering point |
| `active_power_export` | AMS meter | `AmsMainMeterMetric.ACTIVE_POWER_EXPORT` | W | Site exporting to grid | Utility metering point |
| `pvpowerin` | Growatt | `PvGrowattMetric.DC_POWER_IN` | W | Solar DC harvest | Inverter DC input (all MPPTs) |
| `pvpowerout` | Growatt | `PvGrowattMetric.AC_POWER_OUT` | W | Solar AC output | Inverter AC output |
| `pv{n}watt` | Growatt | `PvGrowattMetric.PV{n}_WATT` | W | Per-tracker DC power | Individual MPPT tracker |

