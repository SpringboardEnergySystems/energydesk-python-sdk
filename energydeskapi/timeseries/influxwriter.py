"""Thin synchronous InfluxDB writer for EnergyDesk asset timeseries.

Usage
-----
from energydeskapi.timeseries.influxwriter import build_influx_sink

writer = build_influx_sink(bucket="mycustomer_assetdata")
try:
    writer.ping()   # raises RuntimeError if unreachable / wrong token
    writer.write_api.write(bucket=writer.bucket, org=writer.org, record=point)
finally:
    writer.close()

Environment variables
---------------------
URL resolution (first match wins):
  INFLUXDB_URL          Full base URL, e.g. http://linux67-dbserver:8086
  INFLUXDB_HOST +
  INFLUXDB_PORT         Assembled into http://{host}:{port}  (port default: 8086)
  (neither set)         Falls back to http://localhost:8086

Authentication:
  INFLUXDB_TOKEN        API token (required for InfluxDB 2.x)

Organisation:
  INFLUXDB_ORG          Organisation name (default: springboard)

Bucket (first match wins):
  explicit bucket=      Passed directly to build_influx_sink()
  INFLUXDB_BUCKET       Env var
  INFLUXDB_DATABASE     Alias used by InfluxDB 1.x / docker-compose setups
  (none set)            Falls back to springboard_assetdata

Note on INFLUXDB_USER / INFLUXDB_PASSWORD
-----------------------------------------
These are the InfluxDB 1.x basic-auth credentials.  The influxdb-client v2
library used here authenticates via token only.  If you are running InfluxDB
2.x (which uses tokens) your INFLUXDB_TOKEN is what matters.  If you are
running InfluxDB 1.8 in compatibility mode, your token is typically
"{INFLUXDB_USER}:{INFLUXDB_PASSWORD}" — set INFLUXDB_TOKEN to that value.

Bucket naming convention
------------------------
Production and sales forecast data for a customer are written to a single
bucket named ``{customer_name}_assetdata``.  Pass the bucket name explicitly::

    writer = build_influx_sink(bucket="aademo_assetdata")

The bucket must exist before writing.  Use ``ensure_bucket_exists()`` to
create it programmatically on first run.
"""

from __future__ import annotations

import logging

import environ

logger = logging.getLogger(__name__)
env = environ.Env()


class _InfluxWriter:
    """Thin synchronous InfluxDB writer.

    Wraps ``influxdb_client.InfluxDBClient`` and exposes the ``write_api``
    plus the bucket/org strings so callers do not need to pass them
    separately to every write call.
    """

    def __init__(self, url: str, token: str, org: str, bucket: str) -> None:
        from influxdb_client import InfluxDBClient
        from influxdb_client.client.write_api import SYNCHRONOUS

        self._client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self._client.write_api(write_options=SYNCHRONOUS)
        self.bucket = bucket
        self.org = org
        self._url = url
        self._token = token

    def ping(self) -> None:
        """Verify connectivity and token validity.

        Calls the InfluxDB ``/health`` endpoint (no auth required) to confirm
        the server is reachable, then calls ``/api/v2/buckets?limit=1`` with
        the configured token to confirm the token is accepted.

        Raises
        ------
        RuntimeError
            With a human-readable message describing exactly what failed:
            unreachable server, authentication error, or unexpected response.
        """
        import urllib.request
        import urllib.error
        import json as _json

        # 1. Reachability — /health needs no token
        health_url = self._url.rstrip("/") + "/health"
        try:
            with urllib.request.urlopen(health_url, timeout=5) as resp:
                body = _json.loads(resp.read())
                if body.get("status") != "pass":
                    raise RuntimeError(
                        "InfluxDB at {} reports unhealthy status: {!r}".format(
                            self._url, body.get("status")
                        )
                    )
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Cannot reach InfluxDB at {} — is the server running and the "
                "hostname/port correct? ({})".format(self._url, exc.reason)
            ) from exc

        # 2. Token check — GET /api/v2/buckets?limit=1
        buckets_url = self._url.rstrip("/") + "/api/v2/buckets?limit=1"
        req = urllib.request.Request(
            buckets_url,
            headers={"Authorization": "Token {}".format(self._token)},
        )
        try:
            with urllib.request.urlopen(req, timeout=5):
                pass  # 200 OK — token accepted
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise RuntimeError(
                    "InfluxDB token rejected (HTTP {}). "
                    "Check INFLUXDB_TOKEN and that the token has write "
                    "permissions on org '{}'.  "
                    "If running InfluxDB 1.8 in compatibility mode, "
                    "INFLUXDB_TOKEN should be 'user:password'.".format(
                        exc.code, self.org
                    )
                ) from exc
            raise RuntimeError(
                "Unexpected HTTP {} from InfluxDB token check at {}.".format(
                    exc.code, buckets_url
                )
            ) from exc

        logger.info(
            "InfluxDB ping OK — url=%s  org=%s  bucket=%s",
            self._url, self.org, self.bucket,
        )

    def close(self) -> None:
        """Close the underlying HTTP client.  Call when done writing."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _resolve_url() -> str:
    """Build the InfluxDB base URL from environment variables.

    Resolution order:
    1. ``INFLUXDB_URL``              e.g. ``http://linux67-dbserver:8086``
    2. ``INFLUXDB_HOST`` + ``INFLUXDB_PORT``   assembled into ``http://{host}:{port}``
    3. ``http://localhost:8086``     hard fallback
    """
    url = env.str("INFLUXDB_URL", default="")
    if url:
        return url
    host = env.str("INFLUXDB_HOST", default="")
    if host:
        port = env.str("INFLUXDB_PORT", default="8086")
        return "http://{}:{}".format(host, port)
    return "http://localhost:8086"


def _resolve_bucket(explicit: str | None) -> str:
    """Resolve the target bucket name.

    Resolution order:
    1. ``explicit``           passed directly to ``build_influx_sink()``
    2. ``INFLUXDB_BUCKET``    env var
    3. ``INFLUXDB_DATABASE``  alias used by InfluxDB 1.x / docker-compose
    4. ``springboard_assetdata``   hard fallback
    """
    if explicit:
        return explicit
    bucket = env.str("INFLUXDB_BUCKET", default="")
    if bucket:
        return bucket
    database = env.str("INFLUXDB_DATABASE", default="")
    if database:
        return database
    return "springboard_assetdata"


def build_influx_sink(bucket: str | None = None) -> _InfluxWriter:
    """Build an ``_InfluxWriter`` from environment variables.

    See module docstring for the full list of accepted env vars and their
    resolution order.

    Parameters
    ----------
    bucket:
        Target bucket name.  When provided this overrides all env vars.
        The recommended naming convention is ``"{customer_name}_assetdata"``.

    Returns
    -------
    _InfluxWriter
        A ready-to-use writer.  Call ``.ping()`` before writing to verify
        connectivity and token validity.  The caller is responsible for
        calling ``.close()`` (or using it as a context manager) when done.

    Raises
    ------
    environ.ImproperlyConfigured
        If ``INFLUXDB_TOKEN`` is not set in the environment.
    """
    url = _resolve_url()
    org = env.str("INFLUXDB_ORG", default="springboard")
    resolved_bucket = _resolve_bucket(bucket)
    token = env.str("INFLUXDB_TOKEN")   # raises ImproperlyConfigured if absent

    logger.info(
        "InfluxDB config — url=%s  org=%s  bucket=%s",
        url, org, resolved_bucket,
    )

    return _InfluxWriter(url=url, token=token, org=org, bucket=resolved_bucket)


def ensure_bucket_exists(
    writer: _InfluxWriter,
    retention_seconds: int = 0,
) -> None:
    """Create ``writer.bucket`` in InfluxDB if it does not already exist.

    Safe to call on every demo setup run — it is a no-op when the bucket
    is already present.

    Parameters
    ----------
    writer:
        An ``_InfluxWriter`` instance (provides URL, token, org, bucket).
    retention_seconds:
        Retention policy in seconds.  ``0`` means infinite retention
        (InfluxDB default).  Pass e.g. ``365 * 24 * 3600`` for 1 year.

    Raises
    ------
    influxdb_client.rest.ApiException
        On unexpected HTTP errors (422 "bucket already exists" is silently
        ignored as a no-op).
    """
    from influxdb_client import InfluxDBClient, BucketRetentionRules
    from influxdb_client.rest import ApiException

    logger.info(
        "Ensuring InfluxDB bucket exists — url=%s  org='%s'  bucket='%s'",
        writer._url, writer.org, writer.bucket,
    )

    client = InfluxDBClient(url=writer._url, token=writer._token, org=writer.org)
    buckets_api = client.buckets_api()
    try:
        existing = buckets_api.find_buckets(name=writer.bucket)
        if existing and existing.buckets:
            logger.info("InfluxDB bucket '%s' already exists — skipping creation.", writer.bucket)
            return
        retention = (
            [BucketRetentionRules(type="expire", every_seconds=retention_seconds)]
            if retention_seconds > 0
            else []
        )
        buckets_api.create_bucket(
            bucket_name=writer.bucket,
            org=writer.org,
            retention_rules=retention,
        )
        logger.info("Created InfluxDB bucket '%s' in org '%s'.", writer.bucket, writer.org)
    except ApiException as exc:
        if exc.status == 422:
            logger.info(
                "InfluxDB bucket '%s' already exists (422) — skipping.", writer.bucket
            )
        else:
            raise
    finally:
        client.close()
