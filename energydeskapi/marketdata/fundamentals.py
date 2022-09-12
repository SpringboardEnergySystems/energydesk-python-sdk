import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)

class Fundamentals:
    """Description...

      """

    @staticmethod
    def query_unavailable_production(base_url, token, period_from, period_until):
        """Queries unavailable productions

        :param base_url: prefix of the URL
        :type base_url: str, required
        :param token: API token
        :type token: str, required
        :param period_from: period from
        :type period_from: str, required
        :param period_until: period to
        :type period_until: str, required
        """
        logger.info("Fetching spot forex rates")
        headers = {'Authorization': 'Token ' + token}
        server_url= base_url + '/api/fundamentals/unavailable-production/'
        qry_payload = {
            "period_from": period_from,
            "period_until": period_until
        }
        result = requests.post(server_url, json=qry_payload,   headers=headers)
        if result.status_code==200:
            json_result=result.json()
            events=json_result['unavailability_events']
            df=pd.DataFrame(events)
            return df
        else:
            logger.error("Problens calling EnergyDesk API " + str(result) + " " + result.text)
            return None

if __name__ == '__main__':
    token = "tokenvalue"
    server_url = "https://127.0.0.1:8000"
    df=Fundamentals.query_unavailable_production(server_url, token, "2022-07-01", "2022-07-05")
    print(df)