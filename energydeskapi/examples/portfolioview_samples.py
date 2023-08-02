
import logging
from energydeskapi.portfolios.portfolioviews_api import PortfolioViewsApi
from energydeskapi.types.portfolio_enum_types import PeriodViewGroupingEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.portfolios.portfolio_api import PortfoliosApi
import pandas as pd
from energydeskapi.types.market_enum_types import CommodityTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_period_view(api_conn):
    ut=PortfoliosApi.get_portfolios_embedded(api_conn)
    for u in ut:
        print(u['pk'],u['description'])

    filter={
        "portfolio":'9',
        'contract_filter':'0',
        'view_currency': 'EUR',
        "view_period_from__gte":'2023-01-01',
        "view_period_until__lt": '2029-01-01',
        "resolution":PeriodResolutionEnum.MONTHLY.value,
        "groupby":PeriodViewGroupingEnum.ASSET.value
    }
    print(filter)
    v, df=PortfolioViewsApi.get_period_view_df(api_conn, filter)
    df['GWh'] = df['netvol'] / 1000
    print(df)
    print(df['asset'].unique().tolist())
    #print(df.to_json(orient='split'))

def get_product_view(api_conn):
    filter={'portfolio': "20"}
    view_id,df=PortfolioViewsApi.get_product_view_df(api_conn, filter)
    print(df)


    #df=PortfolioViewsApi.get_product_view_df(api_conn, filter)
    #print(df)
if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()
    get_period_view(api_conn)
