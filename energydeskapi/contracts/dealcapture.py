from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.lems.lems_api import LemsApi
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.types.contract_enum_types import ContractStatusEnum
from energydeskapi.types.market_enum_types import CommodityTypeEnum, DeliveryTypeEnum,MarketEnum, InstrumentTypeEnum
from moneyed import NOK
from energydeskapi.sdk.money_utils import FormattedMoney

def bilateral_dealcapture(api_conn):
    locprods_df=LemsApi.get_traded_products_df(api_conn)

    trades = LemsApi.get_own_trades(api_conn)
    for t in trades:
        #print(t)
        deal_id=t['deal_id']
        trade_id = t['trade_id']
        loc_ticker = t['ticker']

        delivery_from=locprods_df.loc[locprods_df["ticker"] ==loc_ticker, 'delivery_from'].iloc[0]
        delivery_until = locprods_df.loc[locprods_df["ticker"] == loc_ticker, 'delivery_until'].iloc[0]

        price = t['price']
        buy_sell = t['side']
        quantity = t['quantity']
        counterpart = t['counterpart']
        create_at = t['create_at']
        tbs=TradingBooksApi.get_tradingbooks(api_conn, {'page_size':100, 'contract_types':1})
        for tb in tbs['results']:
            print(tb)
        tb=31

        comdef=MarketsApi.get_commodity(api_conn, {'product_code':loc_ticker})
        delivery_type = DeliveryTypeEnum.PHYSICAL
        commodity_type = CommodityTypeEnum.POWER
        contract_status = ContractStatusEnum.REGISTERED
        instrument_type = InstrumentTypeEnum.FWD
        counterpart_dict=CustomersApi.get_companies(api_conn,  {'name__icontains':counterpart})
        if len(counterpart_dict['results'])==0:
            continue

        counterpart_pk=counterpart_dict['results'][0]['pk']
        prof = UsersApi.get_user_profile(api_conn)
        tader_pk = prof['pk']
        c=Contract(trade_id, tb,
                    FormattedMoney(price, NOK),round(quantity, 1),
                    FormattedMoney(0, NOK),
                    FormattedMoney(0, NOK),
                   create_at[0:10],create_at, 
                   commodity_type,
                   instrument_type,
                   contract_status,
                   buy_sell,
                   counterpart_pk,
                   MarketEnum.NORDIC_POWER,
                   tader_pk)
        print(c.get_dict(api_conn))
        c.contract_status = ContractStatusEnum.CONFIRMED
        c.commodity_delivery_from = delivery_from
        c.commodity_delivery_until =delivery_until
        c.product_code = loc_ticker
        c.commodity_profile="BASELOAD"
        ContractsApi.upsert_contract(api_conn,c)

def get_dealcapture_config(api_connection):
    """Fetches dealcapture

    :param api_connection: class with API token for use with API
    :type api_connection: str, required
    """
    json_res = api_connection.exec_get_url('/api/lems/showdealcaptureconfig/')
    if json_res is None:
        return None
    return json_res

def set_dealcapture_config(api_connection, payload):
    """Sets dealcapture

    :param api_connection: class with API token for use with API
    :type api_connection: str, required
    """
    success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/lems/setdealcaptureconfig/',
                                                                                  payload)
    if success:
        return success, returned_data, status_code, error_msg
    return None
