import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)


class GeneralApi:
    """Class for user general portal API information

    """
    @staticmethod
    def get_ticker_text(api_connection):
        """Fetches ticker text to flash on the front portal. This could be general price info or users custom params

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching ticker text")
        json_res=api_connection.exec_get_url('/api/energydesk/tickerinfo/')
        if json_res is not None:
            return json_res['common_ticker']
        return ""
