
import logging
from energydeskapi.portfolios.portfolioviews_api import PortfolioViewsApi
from energydeskapi.types.portfolio_enum_types import PeriodViewGroupingEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.types.market_enum_types import CommodityTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_period_view(api_conn):
    filter={
        "portfolio":76,
        "view_period_from__gte":"2023-02-01",
        "view_period_until__lt": "2023-06-01",
        "resolution":PeriodResolutionEnum.MONTHLY.value,
        "groupby":[PeriodViewGroupingEnum.AREA.value]
    }
    df=PortfolioViewsApi.get_period_view_df(api_conn, filter)
    print(df)
    #print(df.to_json(orient='split'))

def get_product_view(api_conn):
    filter={'portfolio': 5}
    df=PortfolioViewsApi.get_product_view_df(api_conn, filter)
    print(df)

    #df=PortfolioViewsApi.get_product_view_df(api_conn, filter)
    #print(df)
if __name__ == '__main__':
    api_conn=init_api()
    get_period_view(api_conn)
