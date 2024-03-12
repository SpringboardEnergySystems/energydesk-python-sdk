import logging
import requests
import environ
import json
from rauth import OAuth2Service
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.contracts.contracts_api import ContractsApi
from energydeskapi.conversions.elvizlink_api import ElvizLinksApi
from energydeskapi.marketdata.products_api import ProductsApi
from energydeskapi.marketdata.derivatives_api import DerivativesApi
from energydeskapi.types.market_enum_types import MarketPlaceEnum, MarketEnum

import pendulum
logger = logging.getLogger(__name__)
#  Change


# Reuses concept from Elviz conversion mapping data
# Used when a customer who is managed by another portfolio manager can have their own system kept in sync
class EnergyDeskinksApi:
    """Class for converting elviz
"""
    @staticmethod
    def exec_load_energydesk_trades(other_edesk_api_connection, user_mappings, company_mappings, portfolio_mappings, days_back):
        env = environ.Env()
        #{'portfolio_id__in':}
        print(portfolio_mappings)
        tbs=[x['elviz_portfolio_id'] for x in portfolio_mappings]
        params={'trading_book__in':tbs}
        print(params)
        clist=ContractsApi.list_contracts_embedded(other_edesk_api_connection, params)
        print(len(clist['results']))
        return None

    @staticmethod
    def get_latest_energydesk_prices(api_connection, days_back=1):
        t2=pendulum.today("Europe/Paris")
        t1=t2.add(days=-days_back)
        #ProductsApi.
        print(str(t1)[:10], str(t2)[:10])
        df = DerivativesApi.fetch_prices_in_period(api_connection, market_place=MarketPlaceEnum.NASDAQ_OMX.name,
                                                   market_name=None,
                                                   ticker=None, period_from=str(t1)[:10],
                                                   period_until=str(t2)[:10])

        #prods=ProductsApi.get_product_prices_embedded(api_connection)
        print(df)
        #edesk_trades = EnergyDeskinksApi.exec_load_energydesk_trades(usr_maps,comp_maps,port_maps, days_back )
        return None

    @staticmethod
    def get_latest_energydesk_products(api_connection, days_back=1):
        #ProductsApi.
        prods=ProductsApi.get_market_products_embedded(api_connection)
        print(prods)
        #edesk_trades = EnergyDeskinksApi.exec_load_energydesk_trades(usr_maps,comp_maps,port_maps, days_back )
        return None

    @staticmethod
    def get_latest_energydesk_trades(api_connection, other_edesk_api_connection, days_back=1):
        port_maps=ElvizLinksApi.get_portfolio_mappings(api_connection)
        usr_maps=ElvizLinksApi.get_user_mappings(api_connection)
        comp_maps=ElvizLinksApi.get_company_mappings(api_connection)
        #edesk_trades = EnergyDeskinksApi.exec_load_energydesk_trades(other_edesk_api_connection, usr_maps,comp_maps,port_maps, days_back )
        products=EnergyDeskinksApi.get_latest_energydesk_prices(other_edesk_api_connection, days_back)
        #print(products)
        return products

