import pendulum
import logging

import pytz

from energydeskapi.portfolios.portfolioviews_api import PortfolioViewsApi
from energydeskapi.types.portfolio_enum_types import PeriodViewGroupingEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.settlement.settlement_api import SettlementApi
from energydeskapi.sdk.datetime_utils import localize_datetime
from energydeskapi.contracts.contracts_api import ContractsApi
from energydeskapi.types.contract_enum_types import ContractTypeEnum
from energydeskapi.types.common_enum_types import resolution_str_to_pandas_freq
import pandas as pd
from dateutil import parser
from energydeskapi.types.market_enum_types import CommodityTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def get_product_settlement_view(api_conn):

    filter={
        "commodity__delivery_from__gte":'2023-08-01',
        "commodity__delivery_until__lt": '2024-09-01',
        #"resolution":PeriodResolutionEnum.HOURLY.value,
        "groupby__in":[PeriodViewGroupingEnum.TRADEID.value]
    }

    v, df=PortfolioViewsApi.get_product_view_df(api_conn, filter)
    print(df.columns)
    subset = ['ticker', 'trade_id','close', 'unreal', 'avgcost', 'avgcostsell', 'netvol', 'sellvol']
    print(df[subset].sort_values(by=['ticker', 'trade_id']))



def get_settlement_view_data(api_conn):
    payload={
        'contract_type':3,
        "period_from":'2023-07-01',
        "period_until": '2023-08-01',
        "resolution":PeriodResolutionEnum.MONTHLY.value,
        #"groupby__in":[PeriodViewGroupingEnum.COUNTERPART.value,PeriodViewGroupingEnum.TRADEID.value]
    }
    print("Calling")
    result= SettlementApi.get_settlement_data(api_conn, payload)
    print(result)

def get_period_result_view(api_conn):

    filter={
        'view_currency': 'NOK',
        'portfolio':131,
        "view_period_from__gte":'2024-01-01',
        "view_period_until__lt": '2025-01-01',
        "resolution":PeriodResolutionEnum.MONTHLY.value,
     }
    v, df = SettlementApi.get_period_result_view_df(api_conn, filter)
    print(df)

def get_product_result_view(api_conn):

    filter={
        'view_currency': 'NOK',
        'portfolio':131,
        'groupby__in': ["instrument"],
        "view_period_from__gte":'2024-01-01',
        "view_period_until__lt": '2028-01-01',
     }
    v, df = SettlementApi.get_product_result_view_df(api_conn, filter)
    print(df)
    print(df['realized'].groupby('ticker').sum())
def get_fixprice_data(api_conn):

    filter={
        'view_currency': 'NOK',
        'contract_type':ContractTypeEnum.BILAT_FIXPRICE.value,
        #'commodity__area': 'NO1',
        "view_period_from__gte":'2023-07-01',
        "view_period_until__lt": '2023-10-01',
        "resolution":PeriodResolutionEnum.MONTHLY.value,
        "groupby__in":[PeriodViewGroupingEnum.COUNTERPART.value]
       # "groupby__in": [PeriodViewGroupingEnum.COUNTERPART.value, PeriodViewGroupingEnum.TRADEID.value]
    }
    v, df=SettlementApi.get_settlement_view_df(api_conn, filter)
    print(df)   # Dataframe

def get_settlement_view(api_conn):

    filter={
        'view_currency': 'NOK',
        'contract_type':ContractTypeEnum.BILAT_FIXPRICE.value,
        #'commodity__area': 'NO1',
        "view_period_from__gte":'2023-07-01',
        "view_period_until__lt": '2023-10-01',
        "commodity__delivery_from": '2024-01-01',
        #"commodity__delivery_until": '2023-09-01',
        "resolution":PeriodResolutionEnum.MONTHLY.value,
        "groupby__in":[PeriodViewGroupingEnum.COUNTERPART.value,PeriodViewGroupingEnum.TRADEID.value]
    }
    print(filter)
    v, df=SettlementApi.get_settlement_view_df(api_conn, filter)

    subset = ['trade_id', 'counterpart',  'period_from', 'period_until','price', 'value', 'netpos', 'avgcostsell', 'netvol', 'sellvol']
    print(df[subset])

    df_inv=df[subset]
    df_inv=df_inv.rename(columns={'period_from':'invoice_period_from','period_until':'invoice_period_until',
                                  'netvol':'period_volume'})
    contracts=df['trade_id'].unique()
    clist=[int(x) for x in list(contracts)]
    print({'page_size':1000, 'id__in':clist})
    reso=ContractsApi.list_contracts_compact(api_conn, {'page_size':1000, 'id__in':clist})
    contracts=pd.DataFrame(data=eval(reso['results']))
    print(df_inv.columns)
    print(contracts.columns)
    def fill_in_contract_info(row):
        contract_row=contracts[contracts['trade_id']==row['trade_id']]
        row['trade_date'] = localize_datetime(parser.isoparse(contract_row.iloc[0]['trade_date']), "Europe/Oslo")
        row['delivery_from']=localize_datetime(parser.isoparse(contract_row.iloc[0]['delivery_from']),"Europe/Oslo")
        row['delivery_until'] = localize_datetime(parser.isoparse(contract_row.iloc[0]['delivery_until']), "Europe/Oslo")
        row['contract_volume']=contract_row.iloc[0]['volume']
        row['price_area'] = contract_row.iloc[0]['area']
        row['product'] = contract_row.iloc[0]['ticker']
        row['profile'] = contract_row.iloc[0]['profile_type']

        return row
    df_inv=df_inv.apply(fill_in_contract_info, axis=1)
    print(df_inv)
    # Gets a list of contracts pivoted in the period view in order to show more information on them


if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    api_conn=init_api()
    print(resolution_str_to_pandas_freq("Monthly"))
    #get_period_result_view(api_conn)
    get_product_result_view(api_conn)
