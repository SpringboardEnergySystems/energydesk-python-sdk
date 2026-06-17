import pendulum
import logging
from energydeskapi.portfolios.portfolioviews_api import PortfolioViewsApi
from energydeskapi.types.portfolio_enum_types import PeriodViewGroupingEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.portfolios.portfolio_api import PortfoliosApi
import pandas as pd
from energydeskapi.types.market_enum_types import CommodityTypeEnum
from energydeskapi.types.contract_enum_types import ContractTypeEnum
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_period_view(api_conn):
    params = {
        'portfolio_id__in': "34",
        'resolution': 'Monthly',
        'contract_price_currency': 'EUR',
    }
    #pd.set_option('display.max_rows', None)
    #view_id, data = PortfolioViewsApi.get_period_view_df(api_conn, params)
    #print(data)
    #json_res = PortfolioViewsApi.get_period_view(api_conn, params)
    v, df = PortfolioViewsApi.get_period_view_df(api_conn, params)

    print(df)


def get_position_view(api_conn):
    groupby=PortfolioViewsApi.get_position_view_groupby_fields(api_conn)
    print(groupby)

    parameters=\
        {'portfolio': "36",
         "view_currency":"EUR",
         "groupby__in": ['counterpart','blocksize_category','instrument'],
         }
    print(parameters)
    res=PortfolioViewsApi.get_position_view(api_conn, parameters)

    for row in res:
        print(json.dumps(row, indent=2))

    return

    v, df = PortfolioViewsApi.get_period_view_df(api_conn, parameters)
    #jsondata=PortfolioViewsApi.get_position_view(api_conn, parameters)
    print(df)


def get_period_view_test(api_conn):
    ut=PortfoliosApi.get_portfolios_embedded(api_conn)
    for u in ut:
        print(u['pk'],u['description'])   # Just to see ID of portfolios available for next query

    periodview_params={
        "contract_type":3, #  3=Fastpris, 4=GO, ContractTypeEnum.GOO.value,   Remove to get all.
        'view_currency': 'NOK',
        "view_period_from__gte":'2024-01-01',
        "view_period_until__lt": '2026-01-01',
        "resolution":"Monthly",
        "groupby":['area']
    }
    print(filter)
    v, df = PortfolioViewsApi.get_period_view_df(api_conn, filter)
    print(v, df)


def get_period_view_records(api_conn):

    periodview_params={
        'portfolio': "36",
        'view_currency': 'EUR',
        "view_period_from__gte":'2025-01-01',
        "view_period_until__lt": '2027-01-01',
        "resolution":"Monthly",
        "groupby__in": ['contract_owner']
    }
    json_res = PortfolioViewsApi.get_period_view_records(api_conn, periodview_params)
    df=pd.DataFrame(data=json_res)
    print(df)


def get_product_view(api_conn):

    filter={'portfolio': "21", "view_currency":"EUR",
            "trade_date__lte":"2025-08-13","groupby__in": ['trading_book'],
            "commodity__delivery_until__gt":"2025-01-01",
            "commodity__cascaded_date__gte":"2025-01-01"}
    print(filter)
    view_id,data=PortfolioViewsApi.get_product_view(api_conn, filter)
    print(json.dumps(data, indent=2))
    fixed = []
    for rec in data:
        frec = rec.copy()
        # Flatten ticker field if it's a list
        if isinstance(frec.get('ticker'), list) and len(frec['ticker']) >= 2:
            frec['ticker'] = frec['ticker'][0]
            frec['portfolio'] = rec['ticker'][1]
        fixed.append(frec)

    #print(json.dumps(fixed, indent=2))
    df=pd.DataFrame(data=fixed)
    df=df.sort_values(by=['ticker'])
    print(df)
    df.to_csv("product_view.csv")


if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()
    get_period_view(api_conn)
