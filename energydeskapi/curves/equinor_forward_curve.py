import numpy as np
import json
import logging
from datetime import date, timedelta
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pendulum
from scipy.interpolate import CubicSpline, PchipInterpolator

from energydeskapi.marketdata.derivatives_api import DerivativesApi
from energydeskapi.sdk.api_connection import ApiConnection
from energydeskapi.sdk.common_utils import init_api

logger = logging.getLogger(__name__)
#Sets the instruments with price for the full curve. Avoiding overlapping periods for the most part.
instruments = [
    # Weeks
    (date(2023, 8, 7), date(2023, 8, 13), 32.25),
    (date(2023, 8, 14), date(2023, 8, 20), 37.00),
    (date(2023, 8, 21), date(2023, 8, 27), 38.00),
    (date(2023, 8, 28), date(2023, 9, 3), 39.00),
    (date(2023, 9, 4), date(2023, 9, 10), 42.00),
    (date(2023, 9, 11), date(2023, 9, 17), 42.00),
    # (date(2023, 8, 1), date(2023, 1, 1),  37.00),  # Removed - invalid date range
    #Months
(date(2023, 8, 1), date(2023, 9, 1),  37.00),
(date(2023, 9, 1), date(2023, 10, 1),  45.35),
(date(2023, 10, 1), date(2023, 11, 1),  47.00),
(date(2023, 11, 1), date(2023, 12, 1),  54.25),
(date(2023, 12, 1), date(2024, 1, 1),  67.50),
(date(2024, 1, 1), date(2024, 2, 1),  83.50),
    # Quarters
(date(2023, 10, 1), date(2024, 1, 1),  56.35),
(date(2024, 1, 1), date(2024, 4, 1),  71.75),
(date(2024, 4, 1), date(2024, 7, 1),  51.18),
(date(2024, 7, 1), date(2024, 10, 1),  34.00),
(date(2024, 10, 1), date(2025, 1, 1),  66.50),
(date(2025, 1, 1), date(2025, 4, 1),  81.85),
(date(2025, 4, 1), date(2025, 7, 1), 44.00),
(date(2025, 7, 1), date(2025, 10, 1),   36.00),
(date(2025, 10, 1), date(2026, 1, 1),  55.00),
# Year
(date(2024, 1, 1), date(2025, 1, 1),   56.25),
(date(2025, 1, 1), date(2026, 1, 1),  54.50),
(date(2026, 1, 1), date(2027, 1, 1),  45.75),
(date(2027, 1, 1), date(2028, 1, 1),  40.75),
(date(2028, 1, 1), date(2029, 1, 1),  39.00),
(date(2029, 1, 1), date(2030, 1, 1),  38.50),
(date(2030, 1, 1), date(2031, 1, 1),  38.50),
(date(2031, 1, 1), date(2032, 1, 1),  38.00)
]

# Seasonal adjustment factors (quarterly ratios: Q1=Winter, Q2=Spring, Q3=Summer, Q4=Fall)
quarterly_multipliers = {
    1: 1.56,  # Q1 - Winter (high prices)
    2: 0.85,  # Q2 - Spring (low prices)
    3: 0.59,  # Q3 - Summer (lowest prices)
    4: 1.00,  # Q4 - Fall (baseline)
}

# Day-of-week multipliers (average=1.0)
dow_multipliers = {
    0: 1.02,  # Monday
    1: 1.05,  # Tuesday
    2: 1.05,  # Wednesday
    3: 1.02,  # Thursday
    4: 0.93,  # Friday
    5: 0.92,  # Saturday
    6: 1.01,  # Sunday
}

def load_instrument_prices(api_connection: ApiConnection, trading_date_iso:str):
    """Load all products from the API."""
    def __convert_date(strdate):
        return pendulum.parse(strdate).in_tz("Europe/Oslo").date()

    params={"price_date": trading_date_iso,'product__commodity_definition__market__name':'NORDIC_POWER',
            'product__commodity_definition__structure_type__code':'PLAIN',
            'product__commodity_definition__instrument_type__code':'FUT',
            'product__market_place__description':'NASDAQ_OMX','page_size':1000}

    data=DerivativesApi.get_prices_embedded_json(api_connection, params)
    print(json.dumps(data['results'], indent=2  ))
    outdata=[]
    for rec in data['results']:
        if rec['close'] is not None and rec['product']['commodity_definition']['block_size_category']['code'] != 'DAY':
            outdata.append((__convert_date(rec['product']['commodity_definition']['delivery_from']),__convert_date(rec['product']['commodity_definition']['delivery_until']),float(rec['close'])))
            print(float(rec['close']))
    return outdata


def build_curvy_forward_curve(instruments_data: List[Tuple[date, date, float]],
                              trading_date: date = None) -> Tuple[List[date], List[float]]:
    """
    Build a forward curve using Equinor's curvy library.

    Curvy uses a builder pattern and creates smooth forward curves (SMFC) by solving
    an optimization problem that maintains correct averages for each period.

    Args:
        instruments_data: List of tuples (start_date, end_date, price)
        trading_date: The valuation/trading date (defaults to today)

    Returns:
        Tuple of (dates, smoothed_prices) - daily values from the curve
    """
    try:
        from curvy import builder, axis
    except ImportError:
        raise ImportError(
            "curvy library not installed.\n"
            "Install with:\n"
            "  cd /Users/steinar/PycharmProjects/curvy\n"
            "  python3.13 -m pip install -e ."
        )

    if trading_date is None:
        trading_date = date.today()

    # Convert our instruments to curvy format
    # Curvy expects a list of forward prices and uses date ranges
    # We need to create date ranges and corresponding prices

    # Sort instruments by start date
    sorted_instruments = sorted(instruments_data, key=lambda x: x[0])

    # Extract prices (curvy will auto-assign to DA, BOM, EOM1, EOM2, etc.)
    forward_prices = [price for _, _, price in sorted_instruments]

    # Calculate number of months to cover
    if sorted_instruments:
        last_end = max(end for _, end, _ in sorted_instruments)
        months_ahead = ((last_end.year - trading_date.year) * 12 +
                       (last_end.month - trading_date.month) + 1)
    else:
        months_ahead = 12  # Default to 1 year

    logger.info(f"Building curvy SMFC with {len(forward_prices)} forward prices over {months_ahead} months")

    # Build the smooth forward curve using curvy's builder
    # This returns: x (dates), y (original prices), dr (date ranges), pr (price ranges), y_smfc (smoothed curve)
    try:
        x, y, dr, pr, y_smfc = builder.build_smfc_curve(
            forward_prices,
            trading_date,
            corr_avg=True  # Correct averages for better accuracy
        )
        logger.info(f"Successfully built curve with {len(x)} daily points")
        return x, y_smfc
    except Exception as e:
        logger.error(f"Failed to build curve with curvy: {e}")
        raise RuntimeError(
            f"Could not build curve with curvy.builder.build_smfc_curve().\n"
            f"Error: {e}\n"
            f"Forward prices: {forward_prices}\n"
            f"Trading date: {trading_date}"
        )


def get_daily_prices_from_curve(dates: List[date],
                                 prices: List[float],
                                 start_date: date = None,
                                 end_date: date = None) -> pd.DataFrame:
    """
    Convert curvy curve output (dates and prices) to a DataFrame.

    Args:
        dates: List of dates from curvy (x values)
        prices: List of smoothed prices from curvy (y_smfc values)
        start_date: Optional filter for start date
        end_date: Optional filter for end date

    Returns:
        DataFrame with columns: date, price, day_of_week, month, quarter
    """
    # Create DataFrame from the curve data
    df = pd.DataFrame({
        'date': dates,
        'price': prices
    })

    # Filter by date range if provided
    if start_date:
        df = df[df['date'] >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df['date'] <= pd.Timestamp(end_date)]

    # Add temporal features
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter

    # Convert date back to date objects
    df['date'] = df['date'].dt.date

    logger.info(f"Converted curve to DataFrame with {len(df)} daily prices")
    return df


def apply_seasonal_adjustments(df: pd.DataFrame,
                               use_quarterly: bool = True,
                               use_dow: bool = True) -> pd.DataFrame:
    """
    Apply seasonal and day-of-week adjustments to daily prices.

    Args:
        df: DataFrame with date, price, quarter, day_of_week columns
        use_quarterly: Whether to apply quarterly multipliers
        use_dow: Whether to apply day-of-week multipliers

    Returns:
        DataFrame with adjusted_price column added
    """
    df = df.copy()
    df['adjusted_price'] = df['price']

    if use_quarterly:
        # Apply quarterly multipliers
        df['quarterly_mult'] = df['quarter'].map(quarterly_multipliers)
        df['adjusted_price'] *= df['quarterly_mult']

    if use_dow:
        # Apply day-of-week multipliers
        df['dow_mult'] = df['day_of_week'].map(dow_multipliers)
        df['adjusted_price'] *= df['dow_mult']

    logger.info(f"Applied seasonal adjustments (quarterly={use_quarterly}, dow={use_dow})")
    return df


def plot_forward_curve(df: pd.DataFrame,
                       instruments_data: List[Tuple[date, date, float]] = None,
                       title: str = "Forward Price Curve"):
    """
    Plot the forward curve with optional instrument prices overlay.

    Args:
        df: DataFrame with date and price columns
        instruments_data: Optional list of instrument tuples to overlay
        title: Plot title
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot daily curve
    ax.plot(df['date'], df['price'], label='Forward Curve', linewidth=2, color='blue', alpha=0.7)

    # Plot adjusted prices if available
    if 'adjusted_price' in df.columns:
        ax.plot(df['date'], df['adjusted_price'], label='Seasonally Adjusted',
                linewidth=1.5, color='green', alpha=0.7, linestyle='--')

    # Overlay instrument prices if provided
    if instruments_data:
        for start_date, end_date, price in instruments_data:
            # Calculate midpoint for plotting
            mid_date = start_date + (end_date - start_date) / 2
            ax.scatter([mid_date], [price], color='red', s=50, alpha=0.6, zorder=5)

            # Determine instrument type by duration
            duration = (end_date - start_date).days
            if duration <= 7:
                marker = 'W'
            elif duration <= 35:
                marker = 'M'
            elif duration <= 100:
                marker = 'Q'
            else:
                marker = 'Y'

            ax.annotate(marker, (mid_date, price),
                       textcoords="offset points", xytext=(0, 10),
                       ha='center', fontsize=8, alpha=0.7)

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price (EUR/MWh)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


if __name__ == '__main__':
    # Note: API connection requires ENERGYDESK_URL environment variable
    # For this example, we'll use sample data

    # Use sample instruments data
    inst_prices = instruments
    api_conn = init_api()
    trading_date: pendulum.DateTime = pendulum.today(tz="Europe/Oslo").add(days=-98)
    inst_prices=load_instrument_prices(api_conn, trading_date_iso="2025-11-12")

    trading_date_obj = date(2025, 8, 14)  # Match the sample data

    print(f"\n{'='*60}")
    print(f"Building Forward Curve with Equinor curvy Library")
    print(f"{'='*60}\n")

    try:
        # Build forward curve using curvy
        dates, smoothed_prices = build_curvy_forward_curve(inst_prices, trading_date=trading_date_obj)
        print(f"✅ Forward curve built successfully with {len(inst_prices)} instruments")
        print(f"   Generated {len(dates)} daily price points")

        # Convert to DataFrame for easier manipulation
        df_prices = get_daily_prices_from_curve(dates, smoothed_prices)
        print(f"✅ Converted to DataFrame with {len(df_prices)} daily prices")

        # Apply seasonal adjustments
        df_adjusted = apply_seasonal_adjustments(df_prices, use_quarterly=True, use_dow=True)

        # Display sample prices
        print(f"\n{'='*60}")
        print("Sample Daily Prices (First 10 days):")
        print(f"{'='*60}")
        print(df_adjusted.head(10).to_string(index=False))

        print(f"\n{'='*60}")
        print("Price Statistics:")
        print(f"{'='*60}")
        print(f"Base Curve - Min: {df_prices['price'].min():.2f}, Max: {df_prices['price'].max():.2f}, Mean: {df_prices['price'].mean():.2f}")
        print(f"Adjusted   - Min: {df_adjusted['adjusted_price'].min():.2f}, Max: {df_adjusted['adjusted_price'].max():.2f}, Mean: {df_adjusted['adjusted_price'].mean():.2f}")

        # Plot the curve
        print(f"\n{'='*60}")
        print("Generating plot...")
        print(f"{'='*60}")
        fig = plot_forward_curve(df_adjusted, instruments_data=inst_prices,
                                title="Nordic Power Forward Curve (Equinor curvy SMFC)")
        plt.savefig('forward_curve_equinor.png', dpi=150, bbox_inches='tight')
        print("✅ Plot saved to: forward_curve_equinor.png")

        # Show plot if not in non-interactive environment
        try:
            plt.show()
        except:
            print("   (Plot display skipped - non-interactive environment)")

    except ImportError as e:
        print(f"❌ Error: {e}")
        print("\nTo install curvy library, run:")
        print("  cd /Users/steinar/PycharmProjects/curvy")
        print("  python3.13 -m pip install -e .")
    except Exception as e:
        print(f"❌ Error building curve: {e}")
        import traceback
        traceback.print_exc()
