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
- **Auth for FastAPI services** — `energydeskapi.auth`: OIDC login (`FastAPIOIDCAuth`), session authorization (`authorization.py`, `session.py`) and bearer verification shared by every pod

---

## Architecture references

Read these before making structural changes:

- **Platform skills and coding conventions**
  `https://github.com/SpringboardEnergySystems/energydesk-ai-context/blob/main/SKILLS.md`

- **Platform-level architecture**
  `https://github.com/SpringboardEnergySystems/energydesk-ai-context/blob/main/ARCHITECTURE.md`

---

## Identity backends (branch `feature/auth-backends`)

The plan lives in the Flexgateway repo:
`energydesk-flexgateway-service/plans/standalone_identity_and_order_management.md`, section
"1. SDK: identity backends". Read it before touching `energydeskapi/auth/`.

What it changes here, in one paragraph: `FastAPIOIDCAuth` already runs the whole OIDC login
itself; the appserver is only consulted afterwards in `authorization.py` to answer "is this
email registered, which role". That call and the bearer introspection Flexgateway does in
`openadr/vtn_auth.py` become two small protocols in a new `energydeskapi/auth/backends.py`:
a `UserDirectory` (`AppserverDirectory` = today's code; `LocalDirectory` = a resolver callable
the service registers) and a `BearerVerifier` (`IntrospectionVerifier`, `JwksVerifier`,
`PodTokenVerifier`, composed by `VerifierChain`), selected with `AUTH_BACKEND=appserver|local`
and `BEARER_VERIFIERS=...`. A `require_bearer(*scopes)` dependency replaces ad-hoc
`API_INTERNAL_POD_TOKEN` checks in services.

Rules that hold while implementing:
- `AUTH_BACKEND=appserver` must behave exactly as before; `energydeskapi/auth/test_authorization.py`
  passes unchanged.
- `AuthorizedUser`, the session cache and every `require_*` dependency keep their signatures.
- Local verification always validates signature, issuer, audience and expiry. Never reproduce the
  appserver's unsigned-claim lookup (`_authorize_bearer_token_session`'s docstring explains it).
- The SDK never owns a user table; `LocalDirectory` only calls the resolver the service gives it.

---

## ⛔ Non-negotiable git branching policy

> **These rules apply in every session, every time, without exception.**
> This repo does NOT follow the product_develop/product_release pattern used
> by other Energydesk repos. `develop` is the one and only active branch here.

### Branch map

| Branch | Purpose | AI may commit? |
|---|---|---|
| `develop` | Active development — all feature PRs target this | ✅ via feature branch only |
| `product_develop` | Release staging — promoted from `develop` by humans only | ❌ never |
| `product_release` | Production — never touched directly | ❌ never |

### Mandatory session checklist

Run these commands before writing a single line of code:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<task-name>
```

Then work only on that feature branch.

### Hard rules — no exceptions

1. **Never commit directly to `develop`** — always go through a feature branch + PR.
2. **Never use `product_develop` as a base or PR target** — even if you see it in `git branch -a` or it looks like "main" from other repos in this org.
3. **Never push to `product_develop` or `product_release`** for any reason.
4. **Always open PRs targeting `develop`**.
5. **Never merge PRs yourself** — merging is a human-gated step.

### Why this differs from other repos

Other Energydesk repos (`energydesk-rpi-venclient`, portal services, etc.) use
`product_develop` as their active working branch. **This SDK is different** — it has
a simpler branching model with `develop` as the sole working branch. If you are
porting a pattern from another repo's CLAUDE.md, do not port the branch names.

### Commit format

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
  auth/
    auth_fastapi.py        FastAPIOIDCAuth — OIDC login (Azure, Google, Django) with authlib;
                           session cookie + process-local token stores
    authorization.py       AuthorizedUser, authorize_session_user(), require_* dependencies,
                           make_registration_gate() — resolves a session to a role
    session.py             resolve_session() / require_page_session() / require_api_session()
    etrm_authorize.py      the appserver calls (get-user-profile, resolve-google-token)
    backends.py            UserDirectory / BearerVerifier protocols and implementations,
                           require_bearer(), AUTH_BACKEND / BEARER_VERIFIERS env wiring
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
                           BackofficeNamespace, DashboardRole,
                           metric_key(), metric_key_prefix(), nats_subject(),
                           dashboard_scope_prefixes()
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
    MetricDomain, EtrmNamespace, RpiNamespace, BackofficeNamespace,
    metric_key, metric_key_prefix, nats_subject, dashboard_scope_prefixes,
)

# Metric key for MetricSnapshot.query_id
key = metric_key(MetricDomain.ETRM, EtrmNamespace.DATASYNC, "contracts_synced_total")
# → "etrm.datasync.contracts_synced_total"

# NATS subject for an ops event from the VEN server
subj = nats_subject(MetricDomain.RPI, RpiNamespace.VENSERVER, "registration.ok")
# → "ops.event.rpi.venserver.registration.ok"

# Prefix for filtering all RPI metrics in a Grafana query
prefix = metric_key_prefix(MetricDomain.RPI)
# → "rpi."

# All prefixes a dashboard role may query
prefixes = dashboard_scope_prefixes(DashboardRole.TRADING_DESK)
# → ["etrm.trading.", "etrm.marketdata.", "etrm.datasync.", "infra.messaging."]
```

When adding a new domain or namespace, add it here first, then use it in the service.
