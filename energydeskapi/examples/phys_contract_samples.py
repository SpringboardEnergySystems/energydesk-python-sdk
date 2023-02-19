import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract, ContractFilter, ContractTag
from energydeskapi.contracts.dealcapture import bilateral_dealcapture
from energydeskapi.contracts.masteragreement_api import MasterAgreementApi, MasterContractAgreement
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.portfolios.portfolioviews_api import PortfolioViewsApi
from energydeskapi.types.portfolio_enum_types import PeriodViewGroupingEnum
from energydeskapi.types.common_enum_types import PeriodResolutionEnum
import json
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def get_contracts(api_conn, trading_book=None):
    json_contractfilter = ContractsApi.list_contracts_embedded(api_conn, {'trading_book':trading_book})
    print(json.dumps(json_contractfilter, indent=2))

def get_exposure(api_conn, trading_book=None):
    filter={
        "trading_book":trading_book,
        "resolution":PeriodResolutionEnum.DAILY.value,
        "groupby":[PeriodViewGroupingEnum.AREA.value, PeriodViewGroupingEnum.COUNTERPART.value]
    }
    view_dataframe=PortfolioViewsApi.get_period_view_df(api_conn, filter)
    print(view_dataframe)


if __name__ == '__main__':
    api_conn=init_api()
    get_contracts(api_conn, 31)
    #get_exposure(api_conn, 31)
