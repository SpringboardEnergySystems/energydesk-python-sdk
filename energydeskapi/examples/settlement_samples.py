import pendulum
import logging
from energydeskapi.portfolios.portfolioviews_api import PortfolioViewsApi
from energydeskapi.types.portfolio_enum_types import PeriodViewGroupingEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.settlement.settlement_api import SettlementApi
from energydeskapi.contracts.contracts_api import ContractsApi
import pandas as pd
from energydeskapi.types.market_enum_types import CommodityTypeEnum
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_settlement_view(api_conn):

    filter={
        #"portfolio":'6',
        #'contract_filter':'0',
        'view_currency': 'NOK',
        #'commodity__area': 'NO1',
        "view_period_from__gte":'2023-08-14',
        "view_period_until__lt": '2023-09-04',
        "resolution":PeriodResolutionEnum.HOURLY.value,
        #"groupby": PeriodViewGroupingEnum.TRADEID.value,
        "groupby__in":[PeriodViewGroupingEnum.COUNTERPART.value,PeriodViewGroupingEnum.TRADEID.value]
    }
    print(filter)
    v, df=SettlementApi.get_settlement_view_df(api_conn, filter)
    subset = ['counterpart', 'trade_id', 'period_from', 'period_until', 'avgcost', 'avgcostsell', 'sellpos', 'sellvol']
    print(df[subset])


    contracts=df['trade_id'].unique()
    print(list(contracts))
    clist=[int(x) for x in list(contracts)]
    print({'page_size':100, 'id__in':clist})
    print(len(clist))
    reso=ContractsApi.list_contracts_compact(api_conn, {'page_size':100, 'id__in':clist})
    print(reso)


if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()
    get_settlement_view(api_conn)
