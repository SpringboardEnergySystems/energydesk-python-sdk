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

class ForwardCurve:
    """
    Forward curve builder for power markets.
    Handles overlapping instruments and creates smooth interpolated curves.
    """

    def __init__(self, instruments: List[Tuple[date, date, float]]):
        """
        Initialize with list of instruments.
        Each contract is (start_date, end_date, price)
        """
        self.instruments = instruments
        self.df_instruments = self._create_contract_dataframe()

    def _create_contract_dataframe(self) -> pd.DataFrame:
        """Convert instruments to a DataFrame with calculated properties."""
        data = []
        for start, end, price in self.instruments:
            # Handle date ordering issues
            if end < start:
                start, end = end, start

            duration_days = (end - start).days
            data.append({
                'start': start,
                'end': end,
                'price': price,
                'duration_days': duration_days,
                'mid_date': start + timedelta(days=duration_days // 2)
            })

        df = pd.DataFrame(data)
        df = df.sort_values('mid_date').reset_index(drop=True)
        return df

    def bootstrap_daily_curve(self, allow_redundancy: bool = True) -> pd.DataFrame:
        """
        Bootstrap daily prices from overlapping instruments.
        Uses priority system: shorter instruments override longer ones.
        """
        if self.df_instruments.empty:
            return pd.DataFrame()

        # Get date range
        min_date = self.df_instruments['start'].min()
        max_date = self.df_instruments['end'].max()

        # Create daily index
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        daily_prices = pd.DataFrame({'date': date_range})
        daily_prices['price'] = np.nan
        daily_prices['weight'] = 0.0

        # Sort instruments by duration (shorter first = higher priority)
        sorted_instruments = self.df_instruments.sort_values('duration_days')

        # Assign prices with weighted averaging for overlaps
        for _, contract in sorted_instruments.iterrows():
            mask = (daily_prices['date'] >= pd.Timestamp(contract['start'])) & \
                   (daily_prices['date'] < pd.Timestamp(contract['end']))

            if allow_redundancy:
                # Weight by inverse of duration (shorter instruments get more weight)
                weight = 1.0 / max(contract['duration_days'], 1)

                # Weighted average
                daily_prices.loc[mask, 'price'] = np.where(
                    np.isnan(daily_prices.loc[mask, 'price']),
                    contract['price'],
                    (daily_prices.loc[mask, 'price'] * daily_prices.loc[mask, 'weight'] +
                     contract['price'] * weight) / (daily_prices.loc[mask, 'weight'] + weight)
                )
                daily_prices.loc[mask, 'weight'] += weight
            else:
                # Simply override with shorter instruments
                daily_prices.loc[mask, 'price'] = contract['price']
                daily_prices.loc[mask, 'weight'] = 1.0

        return daily_prices[['date', 'price']].dropna()

    def create_smooth_curve(self,
                           method: str = 'pchip',
                           seasonal_adjust: bool = False,
                           dow_adjust: bool = False) -> pd.DataFrame:
        """
        Create a smooth interpolated curve from the bootstrapped data.

        Args:
            method: 'pchip' (monotonic) or 'cubic' (smoother but can overshoot)
            seasonal_adjust: Apply quarterly seasonal adjustments
            dow_adjust: Apply day-of-week adjustments
        """
        # Get bootstrapped daily curve
        daily_curve = self.bootstrap_daily_curve()

        if daily_curve.empty:
            return pd.DataFrame()

        # Create key points for interpolation (using contract midpoints)
        key_points = []
        for _, contract in self.df_instruments.iterrows():
            mid_date = contract['mid_date']
            key_points.append((mid_date, contract['price']))

        # Sort by date and remove duplicates (average prices for same date)
        key_points.sort(key=lambda x: x[0])

        # Group by date and average prices for duplicate dates
        unique_points = {}
        for date, price in key_points:
            if date in unique_points:
                # Average with existing price
                unique_points[date] = (unique_points[date] + price) / 2
            else:
                unique_points[date] = price

        # Convert to sorted lists
        key_dates = sorted(unique_points.keys())
        key_prices = [unique_points[d] for d in key_dates]

        # Need at least 2 points for interpolation
        if len(key_dates) < 2:
            # Fall back to using start and end of instruments
            min_contract_date = self.df_instruments['start'].min()
            max_contract_date = self.df_instruments['end'].max()
            avg_price = self.df_instruments['price'].mean()
            key_dates = [min_contract_date, max_contract_date]
            key_prices = [avg_price, avg_price]

        # Convert to numeric for interpolation
        key_numeric = np.array([(d - key_dates[0]).days for d in key_dates])
        key_prices_array = np.array(key_prices)

        # Create interpolator
        if method == 'pchip':
            interpolator = PchipInterpolator(key_numeric, key_prices_array)
        else:
            interpolator = CubicSpline(key_numeric, key_prices_array)

        # Generate smooth curve for full date range
        min_date = daily_curve['date'].min()
        max_date = daily_curve['date'].max()
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')

        smooth_df = pd.DataFrame({'date': date_range})
        smooth_df['days_from_start'] = (smooth_df['date'] - pd.Timestamp(key_dates[0])).dt.days
        smooth_df['price'] = interpolator(smooth_df['days_from_start'])

        # Apply seasonal adjustments if requested
        if seasonal_adjust:
            smooth_df['quarter'] = smooth_df['date'].dt.quarter
            smooth_df['price'] = smooth_df.apply(
                lambda row: row['price'] * quarterly_multipliers.get(row['quarter'], 1.0),
                axis=1
            )

        # Apply day-of-week adjustments if requested
        if dow_adjust:
            smooth_df['dow'] = smooth_df['date'].dt.dayofweek
            smooth_df['price'] = smooth_df.apply(
                lambda row: row['price'] * dow_multipliers.get(row['dow'], 1.0),
                axis=1
            )

        return smooth_df[['date', 'price']]

    def plot_curves(self,
                   show_instruments: bool = True,
                   show_bootstrapped: bool = True,
                   show_smooth: bool = True,
                   seasonal_adjust: bool = False,
                   dow_adjust: bool = False):
        """Plot the various curve representations."""
        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot instruments as horizontal bars
        if show_instruments:
            for _, contract in self.df_instruments.iterrows():
                ax.plot([contract['start'], contract['end']],
                       [contract['price'], contract['price']],
                       'o-', linewidth=3, alpha=0.4, markersize=4)
            ax.plot([], [], 'o-', linewidth=3, alpha=0.4, label='instruments')

        # Plot bootstrapped daily curve
        if show_bootstrapped:
            daily_curve = self.bootstrap_daily_curve()
            if not daily_curve.empty:
                ax.plot(daily_curve['date'], daily_curve['price'],
                       '-', alpha=0.6, linewidth=1, label='Bootstrapped Daily')

        # Plot smooth curve
        if show_smooth:
            smooth_curve = self.create_smooth_curve(
                seasonal_adjust=seasonal_adjust,
                dow_adjust=dow_adjust
            )
            if not smooth_curve.empty:
                label = 'Smooth Curve'
                if seasonal_adjust:
                    label += ' (Seasonal Adj.)'
                if dow_adjust:
                    label += ' (DOW Adj.)'
                ax.plot(smooth_curve['date'], smooth_curve['price'],
                       '-', linewidth=2, label=label)

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price (€/MWh)', fontsize=12)
        ax.set_title('Power Forward Curve', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        return fig, ax


if __name__ == '__main__':
    api_conn = init_api()
    trading_date: pendulum.DateTime = pendulum.today(tz="Europe/Oslo").add(days=-98)
    inst_prices=load_instrument_prices(api_conn, trading_date_iso="2025-11-12")

    # Create the forward curve object
    curve = ForwardCurve(inst_prices)

    # Plot different variations
    print("Plotting forward curves...")
    print(f"Number of instruments: {len(instruments)}")
    print(f"Date range: {curve.df_instruments['start'].min()} to {curve.df_instruments['end'].max()}")

    #Plot 1: Basic curves
    fig1, ax1 = curve.plot_curves(
         show_instruments=True,
         show_bootstrapped=True,
         show_smooth=True,
         seasonal_adjust=False,
         dow_adjust=False
     )
    plt.figure(fig1.number)
    # plt.savefig('forward_curve_basic.png', dpi=150, bbox_inches='tight')
    # print("Saved: forward_curve_basic.png")

    # Plot 2: With seasonal adjustments
    fig2, ax2 = plt.subplots(figsize=(14, 8))
    smooth_basic = curve.create_smooth_curve(seasonal_adjust=False, dow_adjust=False)
    smooth_seasonal = curve.create_smooth_curve(seasonal_adjust=True, dow_adjust=False)
    smooth_seasonal_dow = curve.create_smooth_curve(seasonal_adjust=True, dow_adjust=True)

    if not smooth_basic.empty:
        ax2.plot(smooth_basic['date'], smooth_basic['price'],
                '-', linewidth=2, label='Smooth (Base)', alpha=0.7)
    if not smooth_seasonal.empty:
        ax2.plot(smooth_seasonal['date'], smooth_seasonal['price'],
                '-', linewidth=2, label='Smooth (Seasonal Adj.)', alpha=0.7)
    if not smooth_seasonal_dow.empty:
        ax2.plot(smooth_seasonal_dow['date'], smooth_seasonal_dow['price'],
                '-', linewidth=1, label='Smooth (Seasonal + DOW Adj.)', alpha=0.5)

    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Price (€/MWh)', fontsize=12)
    ax2.set_title('Power Forward Curve - Comparison of Adjustments', fontsize=14, fontweight='bold')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('forward_curve_adjustments.png', dpi=150, bbox_inches='tight')
    print("Saved: forward_curve_adjustments.png")

    plt.show()
