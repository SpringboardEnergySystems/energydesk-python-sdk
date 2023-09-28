import pendulum
import logging
from energydeskapi.portfolios.portfolioviews_api import PortfolioViewsApi
from energydeskapi.types.portfolio_enum_types import PeriodViewGroupingEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.settlement.settlement_api import SettlementApi
import pandas as pd
from energydeskapi.types.market_enum_types import CommodityTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_settlement_view(api_conn):

    filter={
        "portfolio":'6',
        'contract_filter':'0',
        'view_currency': 'EUR',
        'commodity__area': 'NO1',
        "view_period_from__gte":'2023-02-14',
        "view_period_until__lt": '2023-03-01',
        "resolution":PeriodResolutionEnum.HOURLY.value,
        #"groupby": PeriodViewGroupingEnum.TRADEID.value,
        "groupby__in":[PeriodViewGroupingEnum.COUNTERPART.value,PeriodViewGroupingEnum.TRADEID.value]
    }
    print(filter)
    v, df=SettlementApi.get_settlement_view_df(api_conn, filter)
    print(df)



if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()
    get_settlement_view(api_conn)
