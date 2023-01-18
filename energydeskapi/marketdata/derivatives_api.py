import requests
import logging
import pandas as pd
import json

logger = logging.getLogger(__name__)
#  Change
class DerivativesApi:
    """Class for derivatives

    """

    @staticmethod
    def fetch_markets(api_connection, market_place="Nasdaq OMX"):
        """Fetches markets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param market_place: Nasdaq OMX or other market
        :type market_place: str
        """
        logger.info("Fetching market places")
        json_res = api_connection.exec_get_url('/api/markets/marketplaces/')
        print(json_res)
        markets=[]
        for mplace in json_res:
            logger.info(mplace['name'])
            if mplace['name']==market_place:
                logger.info("Found our main market place; list available markets traded")
                for market_url in mplace['markets']:
                    market_url=market_url.replace("http://dev","https://dev")  # A bug on server not showing https
                    logger.info("Lookup market on URL " + str(market_url))
                    result2 = requests.get(market_url, headers=api_connection.get_authorization_header())
                    market=result2.json()
                    logger.info("Market traded on " + str(market_place) + ": " + str(market['name']))
                    markets.append(market['name'])
        return markets

    @staticmethod
    def get_products_df(api_connection, market_place, market_name, traded_from_date):
        """Fetches products within a specified date

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param market_place: description...
        :type market_place: str, required
        :param market_name: name of market
        :type market_name: str, required
        :param traded_from_date: date from when traded
        :type traded_from_date: str, required
        """
        logger.info("Fetching products traded after date " + str(traded_from_date))
        qry_payload = {
            "market_place": market_place,
            "market_name": market_name,
            "tradingdate_from": traded_from_date,
        }
        success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/markets/query-products-ext/', qry_payload)
        if json_res is not None:
            df = pd.DataFrame(data=json_res)
            logger.debug("Products " + str(df))
            return df
        return None

    @staticmethod
    def fetch_product_prices(base_url, token, market_place, market_name, area=None):
        """Fetches product prices

        :param base_url: prefix of the URL
        :type base_url: str, required
        :param token: API token
        :type token: str, required
        :param market_place: description...
        :type market_place: str, required
        :param market_name: name of market
        :type market_name: str, required
        :param area: area code
        :type area: str
        """
        headers = {'Authorization': 'Token ' +token}
        server_url= base_url + '/api/markets/area-product-prices/'
        logger.info("Fetching product prices in " + market_name)
        qry_payload = {
            "market_place": market_place,
            "market_name": market_name,
            "currency_code": "EUR",
            "area": "ALL" if area is None else area
        }

        result = requests.post(server_url, json=qry_payload, headers=headers)
        if result.status_code!=200:
            logger.error("Problens calling EnergyDesk API " + str(result) + " " + result.text)
            return None
        df = pd.read_json(result.json()['dataframe'], orient='records')
        return df


    @staticmethod
    def fetch_daily_prices(api_connection, market_place, market_name, area=None):
        """Fetches daily prices

        :param base_url: prefix of the URL
        :type base_url: str, required
        :param token: API token
        :type token: str, required
        :param market_place: description...
        :type market_place: str, required
        :param market_name: name of market
        :type market_name: str, required
        :param area: area code
        :type area: str
        """

        logger.info("Fetching daily prices in " + market_name)
        qry_payload = {
            "market_place": market_place,
            "market_name": market_name,
            "currency_code": "EUR",
            "area": "ALL" if area is None else area
        }
        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/markets/area-product-prices/', qry_payload)
        if json_res is None:
            return None
        #df = pd.read_json(result.json()['dataframe'], orient='records')
        df = pd.DataFrame(data=eval(json_res))
        return df

    @staticmethod
    def fetch_prices_in_period(api_connection, market_place, market_name, ticker, period_from, period_until):
        """Fetches price for selected product

        :param base_url: prefix of the URL
        :type base_url: str, required
        :param token: API token
        :type token: str, required
        :param market_place: description...
        :type market_place: str, required
        :param market_name: name of market
        :type market_name: str, required
        :param ticker: description...
        :type ticker: str, required
        :param period_from: period from
        :type period_from: str, required
        :param period_until: period to
        :type period_until: str, required
        """
        logger.info("Fetching prices for product " + str(ticker))


        #server_url = base_url + '/api/markets/derivatives_prices_in_period/'
        logger.info("Fetching prices in " + market_name)
        qry_payload={"currency_code":"EUR"}
        if market_place is not None:
            qry_payload[ "market_place"]=market_place
        if market_name is not None:
            qry_payload[ "market_name"]=market_name
        if ticker is not None:
            qry_payload[ ticker]=ticker
        if period_from is not None:
            qry_payload[ "period_from"]=period_from
        if period_until is not None:
            qry_payload[ "period_until"]=period_until


        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/markets/derivatives-prices-in-period/', qry_payload)

        if not success:

            logger.error("Problens calling EnergyDesk API " + str(status_code) + " " + error_msg)
            return None
        data=json.loads(json_res)
        df = pd.DataFrame(data=data)
        return df

    @staticmethod
    def update_intraday_price(api_connection, market, price_date, df):
        """Fetches price for selected product

        :param base_url: prefix of the URL
        :type base_url: str, required
        :param token: API token
        :type token: str, required
        :param market_place: description...
        :type market_place: str, required
        :param market_name: name of market
        :type market_name: str, required
        :param ticker: description...
        :type ticker: str, required
        :param period_from: period from
        :type period_from: str, required
        :param period_until: period to
        :type period_until: str, required
        """

        logger.info("Fetching counterparts list")
        payload = {'market': market,
                   'price_date': price_date,
                   'intraday_prices': df.to_json(orient='records')
                   }
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
            '/api/markets/update-intraday-prices/', payload)
        if success:
            return returned_data
        return error_msg
