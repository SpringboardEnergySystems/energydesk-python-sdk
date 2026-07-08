from unittest import TestCase
from unittest.mock import patch, MagicMock

import pytest

from energydeskapi.timeseries.timeseries_persister import write_production_forecast_to_influx


class _FakeWriteApi:
    def __init__(self):
        self.records = []

    def write(self, bucket, org, record):
        self.records.append(record)


class _FakeWriter:
    bucket = "celsio_assetdata"
    org = "myorg"

    def __init__(self):
        self.write_api = _FakeWriteApi()


def _fake_post(url, json=None, params=None, headers=None, timeout=None):
    resp = MagicMock()
    resp.status_code = 200
    if url.endswith("/definitions/"):
        resp.json.return_value = {"id": "def-uuid-1"}
    elif url.endswith("/instances/"):
        resp.json.return_value = {"id": "inst-uuid-1"}
    return resp

@pytest.mark.skip(reason="it uses influxdb but we don't have any module for that in Hafslund")
class TestWriteProductionForecastToInflux(TestCase):
    def test_without_catalog_args_writes_no_series_key(self):
        writer = _FakeWriter()
        n = write_production_forecast_to_influx(
            monthly_rows=[{"period": "2026-06", "forecast_production_mwh": 10.0}],
            asset_meta={"pk": 2, "name": "Other", "asset_type": "wind", "owner": "Acme"},
            writer=writer,
        )
        self.assertEqual(n, 1)
        line = writer.write_api.records[0].to_line_protocol()
        self.assertNotIn("series_key", line)

    @patch.dict("os.environ", {"INSIGHT_API_URL": "http://fake", "INSIGHT_API_TOKEN": "tok"})
    @patch("energydeskapi.timeseries.catalog_client.requests.post", side_effect=_fake_post)
    def test_with_catalog_args_tags_series_key(self, _mock_post):
        writer = _FakeWriter()
        n = write_production_forecast_to_influx(
            monthly_rows=[{"period": "2026-06", "forecast_production_mwh": 123.4}],
            asset_meta={"pk": 1, "name": "Iveland", "asset_type": "hydro", "owner": "Acme", "price_area": "NO1"},
            writer=writer,
            customer_id="celsio",
            timeseries_date="2026-07-06",
        )
        self.assertEqual(n, 1)
        line = writer.write_api.records[0].to_line_protocol()
        self.assertIn("series_key=inst-uuid-1", line)

    @patch.dict("os.environ", {"INSIGHT_API_URL": "http://fake", "INSIGHT_API_TOKEN": "tok"})
    @patch("energydeskapi.timeseries.catalog_client.requests.post", side_effect=RuntimeError("boom"))
    def test_catalog_failure_never_blocks_influx_write(self, _mock_post):
        writer = _FakeWriter()
        n = write_production_forecast_to_influx(
            monthly_rows=[{"period": "2026-06", "forecast_production_mwh": 1.0}],
            asset_meta={"pk": 3, "name": "Flaky", "asset_type": "hydro", "owner": "Acme"},
            writer=writer,
            customer_id="celsio",
            timeseries_date="2026-07-06",
        )
        self.assertEqual(n, 1)
        line = writer.write_api.records[0].to_line_protocol()
        self.assertNotIn("series_key", line)
