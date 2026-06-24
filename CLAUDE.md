# CLAUDE.md

This file provides guidance to Claude Code and Claude.ai when working in this repository.

---

## What this project is

**`energydesk-python-sdk`** is the shared Python SDK for all Energydesk platform services.

Key responsibilities:
- **API client** — `ApiConnection` / `ApiTempConnection` for talking to the Energydesk REST API
- **Collector framework** — `NatsBus`, `SinkBundle`, `WorkerConfig`, job registry, worker runner, NATS utilities used by all collector/worker services
- **Domain types** — `energydeskapi.types.domain_types`: the single source of truth for metric domains, namespaces, and dashboard roles shared across all services
- **Enum types** — contract, market, and other domain enums used across services

---

## Architecture references

Read these before making structural changes:

- **Platform skills and coding conventions**
  `https://github.com/SpringboardEnergySystems/energydesk-ai-context/blob/main/SKILLS.md`

- **Platform-level architecture**
  `https://github.com/SpringboardEnergySystems/energydesk-ai-context/blob/main/ARCHITECTURE.md`

---

## ⛔ Non-negotiable git branching policy

> These rules apply in every session, every time, without exception.

**The working branch in this repo is `develop`. Never use `product_develop` as a base or PR target.**

| Branch | Purpose |
|---|---|
| `develop` | Active development — all feature PRs target this |
| `product_develop` | Release staging — promoted from `develop` by humans only |
| `product_release` | Production — never touched directly |

At the start of every session that involves any code changes:

1. Pull the latest `develop`
2. Create and check out a new branch from `develop`:
   ```
   git checkout -b feature/<task-name>
   ```
3. All commits go to the feature branch only
4. Open PR targeting **`develop`** — never `product_develop`
5. The merge is a **human-gated step** — do not merge automatically

**Commit format:**
- `feat:` — new functionality
- `fix:` — bug fix
- `refactor:` — restructuring without behaviour change
- `docs:` — documentation only

> Full workflow reference:
> `https://github.com/SpringboardEnergySystems/energydesk-ai-context/blob/main/wiki/claude_code_branching_workflow.md`

---

## Key modules

```
energydeskapi/
  collector/
    nats_client.py         NatsBus — connect, ensure_stream, publish_json, kv_*
    sinks.py               SinkBundle — carries api, bus, influx, postgres into handlers
    worker_runner.py       run_worker() — main NATS job dispatch loop
    worker_registration.py register_worker() — announces worker to central scheduler
    config.py              WorkerConfig — reads NATS_URL, metrics port, etc. from env
    models.py              JobMessage, WorkerRegistration Pydantic models
    metrics.py             start_metrics_server() — Prometheus /metrics endpoint
  types/
    domain_types.py        MetricDomain, EtrmNamespace, RpiNamespace, InfraNamespace,
                           DashboardRole, metric_key(), nats_subject()
    contract_enum_types.py ContractStatusEnum, ContractTypeEnum, …
    market_enum_types.py   MarketEnum, InstrumentTypeEnum, …
  sdk/
    api_connection.py      ApiConnection, ApiTempConnection
    common_utils.py        key_from_url and other small helpers
```

---

## Metric taxonomy

`domain_types.py` is the single source of truth for metric identifiers across the platform.
All services — emitters and consumers — import from here. Never hand-roll metric strings.

```python
from energydeskapi.types.domain_types import (
    MetricDomain, EtrmNamespace, RpiNamespace, metric_key, nats_subject
)

# Metric key for MetricSnapshot.query_id
key = metric_key(MetricDomain.ETRM, EtrmNamespace.DATASYNC, "contracts_synced_total")
# → "etrm.datasync.contracts_synced_total"

# NATS subject for ops event
subj = nats_subject(MetricDomain.RPI, RpiNamespace.WORKER, "heartbeat.missed")
# → "ops.event.rpi.worker.heartbeat.missed"
```

When adding a new domain or namespace, add it here first, then use it in the service.
