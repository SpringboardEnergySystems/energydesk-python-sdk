import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.conversions.elvizlink_api import ElvizLinksApi
from energydeskapi.sdk.money_utils import FormattedMoney
from energydeskapi.contracts.contracts_api import Contract as ApiContract, ContractTag, ContractsApi
from energydeskapi.marketdata.products_api import ProductsApi
from energydeskapi.types.company_enum_types import CompanyTypeEnum, CompanyRoleEnum
from energydeskapi.types.market_enum_types import MarketEnum, InstrumentTypeEnum
from os.path import join, dirname
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def load_elviz_trades(api_conn):
    elviz_trades = ElvizLinksApi.get_latest_elviz_trades(api_conn, 20)
    contracts = []
    for t in elviz_trades:
        # market_product_key = 0
        # success, json_res, status_code, error_msg = ProductsApi.generate_market_product_from_ticker(api_conn,
        #                                                                                             "Nordic Power",
        #                                                                                             t['commodity']['product_code'])
        contract_obj=ApiContract.from_simple_dict(t)
        contracts.append(contract_obj)
    print(contracts)
    ContractsApi.bulk_insert_contracts(api_conn, contracts)
    return contracts

def get_sessions():
    ElvizLinksApi.obtain_session()


if __name__ == '__main__':

    api_conn=init_api()
    contracts = load_elviz_trades(api_conn)
    #get_sessions()
