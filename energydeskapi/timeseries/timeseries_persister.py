import logging
from datetime import datetime

from energydeskapi.timeseries.influx_schema import (
    production_forecast_point,
    sales_forecast_point,
)

logger = logging.getLogger(__name__)


# ── eSett EXP14 imbalance write helpers ───────────────────────────────────────


def write_production_forecast_to_influx(df, currency: str, writer, resolution: str = "15min") -> int:
    """Write eSett imbalance purchase prices to ``imbalance_purchase_prices``.

    *df* columns: ``area``, ``imbalance_purchase_price``, optionally ``currency``
    (overridden by the *currency* parameter).
    Rows where ``imbalance_purchase_price`` is ``None`` / ``NaN`` are skipped.
    """
    import pandas as pd
    points_written = 0
    for index, row in df.iterrows():
        try:
            val = row.get("imbalance_purchase_price")
            if val is None or (isinstance(val, float) and pd.isna(val)):
                continue
            timestamp = index
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            point = imbalance_purchase_price_point(
                area=row["area"],
                price=val,
                currency=currency,
                timestamp=timestamp,
                resolution=resolution,
            )
            writer.write_api.write(bucket=writer.bucket, org=writer.org, record=point)
            points_written += 1
        except Exception as exc:
            logger.error("Error writing imbalance_purchase_price point: %s, row=%s", exc, row)

    logger.info("Wrote %d imbalance_purchase_price points (%s) to InfluxDB", points_written, currency)
    return points_written


def write_sales_forecast_to_influx(df, currency: str, writer, resolution: str = "15min") -> int:
    """Write eSett imbalance sales prices to ``imbalance_sales_prices``.

    *df* columns: ``area``, ``imbalance_sales_price``.
    Rows where ``imbalance_sales_price`` is ``None`` / ``NaN`` are skipped.
    """
    import pandas as pd
    points_written = 0
    for index, row in df.iterrows():
        try:
            val = row.get("imbalance_sales_price")
            if val is None or (isinstance(val, float) and pd.isna(val)):
                continue
            timestamp = index
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            point = imbalance_sales_price_point(
                area=row["area"],
                price=val,
                currency=currency,
                timestamp=timestamp,
                resolution=resolution,
            )
            writer.write_api.write(bucket=writer.bucket, org=writer.org, record=point)
            points_written += 1
        except Exception as exc:
            logger.error("Error writing imbalance_sales_price point: %s, row=%s", exc, row)

    logger.info("Wrote %d imbalance_sales_price points (%s) to InfluxDB", points_written, currency)
    return points_written



