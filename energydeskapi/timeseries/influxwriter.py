from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

import environ
import pendulum

logger = logging.getLogger(__name__)
env = environ.Env()

class _InfluxWriter:
    """Thin synchronous InfluxDB writer matching the timeseries_persister interface."""

    def __init__(self, url: str, token: str, org: str, bucket: str) -> None:
        from influxdb_client import InfluxDBClient
        from influxdb_client.client.write_api import SYNCHRONOUS

        self._client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self._client.write_api(write_options=SYNCHRONOUS)
        self.bucket = bucket
        self.org = org

    def close(self) -> None:
        self._client.close()


def build_influx_sink() -> _InfluxWriter:
    return _InfluxWriter(
        url=env.str("INFLUXDB_URL", default="http://localhost:8086"),
        token=env.str("INFLUXDB_TOKEN"),
        org=env.str("INFLUXDB_ORG", default="springboard"),
        bucket=env.str("INFLUXDB_BUCKET", default="springboard_tsodata"),
    )