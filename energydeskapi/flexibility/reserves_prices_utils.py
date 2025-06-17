import logging
import json
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.types.asset_enum_types import TimeSeriesTypesEnum
from energydeskapi.types.baselines_enum_types import BaselinesModelsEnums
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.assetdata.assetdata_api import AssetDataApi
import pendulum
from energydeskapi.assetdata.baselines_api import BaselinesApi
from energydeskapi.types.flexibility_enum_types import ExternalMarketTypeEnums
import pandas as pd
from datetime import timezone, datetime, date
import json, pendulum
from energydeskapi.contracts.contracts_api import ContractsApi
from energydeskapi.types.contract_enum_types import QuantityTypeEnum, QuantityUnitEnum
from energydeskapi.types.flexibility_enum_types import RegulationTypeEnums
from json import JSONEncoder
from dataclasses import dataclass
import sys
import plotly.graph_objs as go
logger = logging.getLogger(__name__)


def plot_boxplot_prices(title, df_capacity_prices, df_activation_prices, show_upper_bounds=False):
    fig = go.Figure()
    f = {'price': ['mean', ]}

    df_capacity_prices['hour'] = df_capacity_prices.index.hour
    df_activation_prices['hour'] = df_activation_prices.index.hour
    #for i in range(0,23):
    fig.add_trace(go.Box(
        x=df_capacity_prices.hour,
        y=df_capacity_prices.price,
        name='Capacity',
    ))
    fig.add_trace(go.Box(
        x=df_activation_prices.hour,
        y=df_activation_prices.price,
        name='Activation',
    ))
    fig.update_layout(
        yaxis=dict(
            title=dict(
                text='normalized moisture')
        ), boxmode='group'
       #roup together boxes of the different traces for each value of x
    )
    fig.show()

def plot_prices(title, df_prices, show_upper_bounds=False):
    hours=list(range(0,24))

    from plotly.subplots import make_subplots

    fig = make_subplots(rows=4, cols=3, start_cell="top-left", subplot_titles=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
    for i in range(0,12):
        df_sub_prices = df_prices.loc[df_prices.month == i]
        if len(df_sub_prices)== 0:
            continue
        print(df_sub_prices)
        col=i % 3 + 1
        row = 1 if i < 4 else 2 if i < 7 else 3 if i < 10 else 4
        fig.add_trace(
                        go.Scatter(
                            x=df_sub_prices['hour'],
                            y=df_sub_prices['median'],
                            line=dict(color='rgb(0,100,80)'),
                            mode='lines', name="Month " + str(i),
                        ),row=row, col=col)
        if show_upper_bounds:
            fig.add_trace( go.Scatter(
                                name='Upper Bound',
                                x=df_sub_prices['hour'],
                                y=df_sub_prices['max'],
                                mode='lines',
                                marker=dict(color="#444"),
                                line=dict(width=0),
                                showlegend=False
                            ),row=row, col=col)

            fig.add_trace(go.Scatter(
                                name='Lower Bound',
                                x=df_sub_prices['hour'],
                                y=df_sub_prices['min'],
                                marker=dict(color="#444"),
                                line=dict(width=0),
                                mode='lines',
                                fillcolor='rgba(0,100,80,0.2)',
                                fill='tonexty',
                                showlegend=False
                            ),row=row, col=col)

        fig.add_trace( go.Scatter(
                            name='Q3',
                            x=df_sub_prices['hour'],
                            y=df_sub_prices['q3'],
                            mode='lines',
                            marker=dict(color="#444"),
                            line=dict(width=0),
                            showlegend=False
                        ),row=row, col=col)
        fig.add_trace(go.Scatter(
                            name='Q1',
                            x=df_sub_prices['hour'],
                            y=df_sub_prices['q1'],
                            marker=dict(color="#444"),
                            line=dict(width=0),
                            mode='lines',
                            fillcolor='rgba(0,30,80,0.2)',
                            fill='tonexty',
                            showlegend=False
                        ),row=row, col=col)
    fig.show()

def plot_comparison_prices(df_prices, show_upper_bounds=False):
    from plotly.subplots import make_subplots
    months=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    fig = make_subplots(rows=4, cols=3, start_cell="top-left", subplot_titles=months)
    for i in range(0,12):
        df_sub_prices = df_prices.loc[df_prices.month == (i + 1)]
        if len(df_sub_prices)== 0:
            continue
        print(df_sub_prices)
        col=i % 3 + 1
        row = 1 if i < 3 else 2 if i < 6 else 3 if i < 9 else 4
        fig.add_trace(go.Bar(x=df_sub_prices['hour'], y=df_sub_prices['activation'], opacity=0.6, width=0.7, name=str(months[i]) + ' mFRR EAM',
                    marker_color='rgba(0,100,80,0.2)',hovertemplate='%{y}'),row=row, col=col)
        fig.add_trace(go.Bar(x=df_sub_prices['hour'], y=df_sub_prices['capacity'], width=0.5, marker_color='rgba(0,30,80,0.2)', name=str(months[i]) + ' mFRR CM', text=df_sub_prices['relation'],
                    textposition='outside'),row=row, col=col)
        fig.update_xaxes(title_text="Hour of Day", row=row, col=col)
        fig.update_yaxes(title_text="NOK/MWh", row=row, col=col)
    fig.show()
def plot_comparison_local_capacity_prices(fg_grouped_prices, gridcomps):
    from plotly.subplots import make_subplots
    colors=["#22577a", "#38a3a5", "#57cc99", "#80ed99", "#c7f9cc"]
    #colors=['rgba(0,100,80,0.2)', 'rgba(0,60,70,0.2)', 'rgba(0,30,60,0.2)']
    months=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    fig = make_subplots(rows=4, cols=3, start_cell="top-left", subplot_titles=months)
    for i in range(0,12):
        col=i % 3 + 1
        row = 1 if i < 3 else 2 if i < 6 else 3 if i < 9 else 4
        for idex, comp in enumerate(gridcomps):
            locprices=fg_grouped_prices[comp]
            locprices= locprices.loc[locprices.month == (i + 1)]
            if len(locprices) == 0:
                continue
            hours=set(locprices['hour'].unique())
            all_hours=set(range(0,24))
            missing_hours=list(all_hours.difference(hours))
            print(locprices)
            missing_records=[]
            for m in missing_hours:
                rec={'month': i, 'hour':m, 'mean':0}
                missing_records.append(rec)
            df_missing_prices=pd.DataFrame(missing_records)
            output = pd.concat([locprices, df_missing_prices], ignore_index=True)

            fig.add_trace(go.Bar(x=output['hour'],
                                 marker_color=colors[idex], hovertemplate='Hour %{x}: %{y}',
                                 name=comp + " " + str(months[i][:3]), y= output['mean']), row=row, col=col)
            fig.update_xaxes(title_text="Hour of Day", row=row, col=col)
            fig.update_yaxes(title_text="NOK/MWh", row=row, col=col)

    fig.show()
# Input is resreves prices as received from the API query in flexibility_api
def group_reserves_prices(df_raw_prices):
    data={}
    df_grouped=df_raw_prices.groupby(["reserves_type",'timestamp']).agg({'area':'max','regulating_direction':'max','reserves_category':'max','price':'mean'})
    for tp, new_df in df_grouped.groupby(level=0):
        print(tp,new_df)
        new_df=new_df.reset_index()
        new_df.index=new_df['timestamp']
        new_df=new_df.tz_convert("Europe/Oslo")
        data[tp]={}
        def q1(x):
            return x.quantile(0.25)
        def q3(x):
            return x.quantile(0.75)
        f = {'price': ['max','min','median','mean', q1, q3, 'std',]}
        df1 = new_df.groupby([new_df.index.month, new_df.index.hour]).agg(f)
        print(df1)
        df1.index.set_names(['x','y'], inplace=True) #to avoid duplicate col namne. But need to readd later as well since level is removed
        df1 = df1.reset_index()
        df1.columns = df1.columns.droplevel(0)
        cols=list(df1.columns)
        cols[0],cols[1]="month", "hour"
        df1.columns=cols
        data[tp] = df1

    return data

