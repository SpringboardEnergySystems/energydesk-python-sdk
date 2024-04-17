
import logging
from energydeskapi.portfolios.portfolioviews_api import PortfolioViewsApi
from energydeskapi.types.portfolio_enum_types import PeriodViewGroupingEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.sdk.common_utils import init_api
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_currency_view(api_conn):
    filter={
        "portfolio":42,
        "view_period_from__gte":"2024-02-01",
        "view_period_until__lt": "2025-06-01",
        "resolution":PeriodResolutionEnum.MONTHLY.value,
        "groupby":[PeriodViewGroupingEnum.AREA.value]
    }
    df=PortfolioViewsApi.get_currency_view_df(api_conn, filter)
    print(df)




    #df=PortfolioViewsApi.get_product_view_df(api_conn, filter)
    #print(df)
if __name__ == '__main__':
    pd.set_option('display.max_rows', None)
    api_conn=init_api()
    get_currency_view(api_conn)
