"""Thin synchronous InfluxDB writer for EnergyDesk asset timeseries.

Usage
-----
from energydeskapi.timeseries.influxwriter import build_influx_sink

# Using env vars (INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG)
writer = build_influx_sink(bucket="mycustomer_assetdata")
try:
    writer.ping()   # raises RuntimeError if unreachable / wrong token
    writer.write_api.write(bucket=writer.bucket, org=writer.org, record=point)
finally:
    writer.close()

Environment variables
---------------------
INFLUXDB_URL    InfluxDB base URL (default: http://localhost:8086)
INFLUXDB_TOKEN  Authentication token (required)
INFLUXDB_ORG    Organisation name (default: springboard)
INFLUXDB_BUCKET Fallback bucket name used when build_influx_sink() is called
                without an explicit bucket argument
                (default: springboard_assetdata)

Bucket naming convention
------------------------
Production and sales forecast data for a customer are written to a single
bucket named ``{customer_name}_assetdata``.  This bucket is shared between
both forecast types; the ``forecast_type`` tag on each point distinguishes
them.  Pass the bucket name to ``build_influx_sink()`` explicitly::

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

        Calls the InfluxDB ``/health`` endpoint (no auth required) to check
        the server is reachable, then calls ``/api/v2/buckets`` with the
        configured token to verify the token is accepted.

        Raises
        ------
        RuntimeError
            With a human-readable message describing what failed:
            unreachable server, authentication error, or unexpected response.
            Intended to be called once before starting a write loop so
            misconfigurations are caught immediately rather than silently
            producing zero writes.
        """
        import urllib.request
        import urllib.error
        import json as _json

        # 1. Health check — no token needed, just confirms the server is up.
        health_url = self._url.rstrip("/") + "/health"
        try:
            with urllib.request.urlopen(health_url, timeout=5) as resp:
                body = _json.loads(resp.read())
                if body.get("status") != "pass":
                    raise RuntimeError(
                        "InfluxDB at {} reports unhealthy status: {}".format(
                            self._url, body.get("status")
                        )
                    )
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Cannot reach InfluxDB at {} — is it running? ({})".format(
                    self._url, exc.reason
                )
            ) from exc

        # 2. Auth check — a GET /api/v2/buckets?limit=1 with the token.
        # A 401/403 means bad token; a 200 means we're in.
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
                    "permissions on org '{}'.".format(exc.code, self.org)
                ) from exc
            raise RuntimeError(
                "Unexpected HTTP {} from InfluxDB auth check.".format(exc.code)
            ) from exc

        logger.info(
            "InfluxDB ping OK — url=%s org=%s bucket=%s",
            self._url, self.org, self.bucket,
        )

    def close(self) -> None:
        """Close the underlying HTTP client.  Call when done writing."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def build_influx_sink(bucket: str | None = None) -> _InfluxWriter:
    """Build an ``_InfluxWriter`` from environment variables.

    Parameters
    ----------
    bucket:
        Target bucket name.  When provided this overrides the
        ``INFLUXDB_BUCKET`` environment variable.  The recommended naming
        convention is ``"{customer_name}_assetdata"``.

    Returns
    -------
    _InfluxWriter
        A ready-to-use writer.  The caller is responsible for calling
        ``.close()`` (or using it as a context manager) when finished.

    Raises
    ------
    environ.ImproperlyConfigured
        If ``INFLUXDB_TOKEN`` is not set in the environment.
    """
    resolved_bucket = bucket or env.str("INFLUXDB_BUCKET", default="springboard_assetdata")
    return _InfluxWriter(
        url=env.str("INFLUXDB_URL", default="http://localhost:8086"),
        token=env.str("INFLUXDB_TOKEN"),
        org=env.str("INFLUXDB_ORG", default="springboard"),
        bucket=resolved_bucket,
    )


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
    RuntimeError
        If the token does not have permission to list or create buckets.
    influxdb_client.rest.ApiException
        On other unexpected HTTP errors (422 "bucket already exists" is
        silently ignored).
    """
    from influxdb_client import InfluxDBClient, BucketRetentionRules
    from influxdb_client.rest import ApiException

    logger.info(
        "Ensuring InfluxDB bucket exists — url=%s org='%s' bucket='%s'",
        writer._url, writer.org, writer.bucket,
    )

    client = InfluxDBClient(
        url=writer._url,
        token=writer._token,
        org=writer.org,
    )
    buckets_api = client.buckets_api()
    try:
        existing = buckets_api.find_buckets(name=writer.bucket)
        if existing and existing.buckets:
            logger.info("InfluxDB bucket '%s' already exists — skipping creation.", writer.bucket)
            return
        retention = [
            BucketRetentionRules(type="expire", every_seconds=retention_seconds)
        ] if retention_seconds > 0 else []
        buckets_api.create_bucket(
            bucket_name=writer.bucket,
            org=writer.org,
            retention_rules=retention,
        )
        logger.info("Created InfluxDB bucket '%s' in org '%s'.", writer.bucket, writer.org)
    except ApiException as exc:
        if exc.status == 422:
            logger.info(
                "InfluxDB bucket '%s' already exists (422) — skipping.",
                writer.bucket,
            )
        else:
            raise
    finally:
        client.close()
