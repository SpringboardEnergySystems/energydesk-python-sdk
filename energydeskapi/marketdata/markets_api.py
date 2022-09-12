import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)


class MarketsApi:
    """Class for user profiles and companies

    """



    @staticmethod
    def get_market_object(api_connection, market_enum):
        """Fetches all company objects with URL relations. Will only return companies for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/markets/' + str(market_enum.value) + "/")
        if json_res is None:
            return None
        return json_res
