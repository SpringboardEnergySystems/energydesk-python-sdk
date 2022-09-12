import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class MoneyMarkets:
    """Description...

    """

    @staticmethod
    def fetch_forex_spot_rates(base_url, token):
        """Fetches forex spot rates

        :param base_url: prefix of the URL
        :type base_url: str, required
        :param token: API token
        :type token: str, required
        """
        logger.info("Fetching spot forex rates")
        headers = {'Authorization': 'Token ' + token}
        server_url= base_url + '/api/moneymarkets/spot_forex_rates/'
        qry_payload = {
            "period_from": "2019-01-01",
            "period_until": "2022-06-01",
        }
        result = requests.post(server_url, json=qry_payload,   headers=headers)
        if result.status_code==200:
            df = pd.read_json(result.json()['dataframe'], orient='records')
            logger.debug("Forex " + str(df))
            return df
        else:
            logger.error("Problens calling EnergyDesk API " + str(result) + " " + result.text)
            return None

    @staticmethod
    def fetch_zero_coupon_rates(base_url, token):
        """Fetches zero coupon rates

        :param base_url: prefix of the URL
        :type base_url: str, required
        :param token: API token
        :type token: str, required
        """
        logger.info("Fetching zero coupon rates")
        t="LqXReN1nGU4MUKzuz2kKkIrS1yI0tR"

        headers = {'Authorization': 'Bearer ' +t}
        server_url=base_url + '/api/moneymarkets/zero_coupon_rates/'
        qry_payload = {
            "period_from": "2019-01-01",
            "period_until": "2022-06-01",
        }
        print(headers)
        result = requests.post(server_url, json=qry_payload,   headers=headers)
        try:
            resp_content = result.json()
        except ValueError:
            resp_content = result.content
            import os
            import webbrowser
            path = os.path.abspath('temp.html')
            url = 'file://' + path
            with open(path, 'w') as f:
                uu = resp_content.decode('utf8')
                #s = uu.encode('cp1250')
                f.write(uu)
            webbrowser.open(url)

        if result.status_code==200:
            df = pd.read_json(result.json()['dataframe'], orient='records')
            logger.debug("Zero coupon rates " + str(df))
            return df
        else:
            logger.error("Problens calling EnergyDesk API " + str(result) + " " + result.text)
            return None
