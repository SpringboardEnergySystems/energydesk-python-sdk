import requests
import json
import logging
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
#  Change
class ClearingApi:
    """Class for clearing reports

    """

    @staticmethod
    def query_clearing_report_data(api_connection, clearing_house, clearing_report_type, from_date, to_date):
        """Queries clearing data between a set time

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param clearing_house: description...
        :type clearing_house: str, required
        :param clearing_report_type: type of clearing report
        :type clearing_report_type: str, required
        :param from_date: date and time from
        :type from_date: str, required
        :param to_date: date and time to
        :type to_date: str, required
        """
        logger.info("Querying clearing report types")
        crtype_pk = clearing_report_type if isinstance(clearing_report_type, int) else clearing_report_type.value
        payload = {"clearing_house": clearing_house,
                   "clearing_report_type": crtype_pk,
                   "from_datetime": from_date,
                   "to_datetime": to_date}
        json_res = api_connection.exec_post_url('/api/clearing/query-clearing-report-data/', payload)
        print(json_res)

        return True

    @staticmethod
    def get_clearing_reports(api_connection):
        """Fetches a list of clearing reports

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching clearing reports list")
        json_res = api_connection.exec_get_url('/api/clearing/reports/')
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_clearing_report_types(api_connection):
        """Fetches a list of clearing report types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching clearing report types list")
        json_res = api_connection.exec_get_url('/api/clearing/reporttypes/')
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df