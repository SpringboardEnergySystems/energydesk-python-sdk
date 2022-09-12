import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class SpotPrices:
    """Class for spot prices

    """

    @staticmethod
    def fetch_spot_prices(base_url, token, market_place, period_from, period_until):
        """Fetches spot prices

        :param base_url: prefix of the URL
        :type base_url: str, required
        :param token: API token
        :type token: str, required
        :param market_place: description...
        :type market_place: str, required
        :param period_from: period from
        :type period_from: str, required
        :param period_until: period to
        :type period_until: str, required
        """
        logger.info("Fetching spot prices")
        headers = {'Authorization': 'Token ' + token}
        server_url = base_url + '/api/markets/spot_prices_in_period/'

        qry_payload = {
            "market_place": market_place,
            "period_from": period_from,
            "period_until": period_until,
            "currency_code": "NOK",
            "market_name": "NOK",
        }


        result = requests.post(server_url, json=qry_payload, headers=headers)
        if result.status_code!=200:
            logger.error("Problens calling EnergyDesk API " + str(result) + " " + result.text)
            return None
        df = pd.read_json(result.json()['dataframe'], orient='records')
        return df


