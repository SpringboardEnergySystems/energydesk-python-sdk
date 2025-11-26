import logging

from energydeskapi.sdk.api_connection import ApiConnection
import time
from requests.exceptions import ChunkedEncodingError
from urllib3.exceptions import IncompleteRead
import requests
logger = logging.getLogger(__name__)

def exec_get_url(api_connection, trailing_url, parameters):
    headers = api_connection.get_authorization_header()

    server_url: str = api_connection.add_trailing_slash_if_missing(api_connection.get_base_url() + trailing_url)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Increase timeout significantly
            response = requests.get(
                server_url,
                headers=headers,
                params=parameters,
                timeout=(30, 600),  # 30s connect, 600s read
                stream=True  # Enable streaming
            )

            # Manually consume response to handle incomplete reads
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content += chunk

            response._content = content
            return response.json()

        except (ChunkedEncodingError, IncompleteRead) as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                raise

            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Incomplete read on attempt {attempt + 1}/{max_retries}, retrying in {wait_time}s...")
            time.sleep(wait_time)

    return None

class DwhApi:
    """Class for user access to Datawarehouse
    """
    @staticmethod
    def get_contract_dimension(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  contracts
        """
        json_res = api_connection.exec_get_url('/api/dwh/contracts/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def get_report_dimension(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/reports/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_timestamp_dimension(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/times/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_contract_timeseries(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/contracttimeseries/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_periodview_timeseries(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        if 'report_date' in parameters:
            json_res = api_connection.exec_get_url('/api/dwh/periodviewtimeseries/', parameters)
        else:
            json_res = api_connection.exec_get_url('/api/dwh/periodviewtimeseries/latest/', parameters)
        logger.info(f"DWH json_res:{json_res}")
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def get_productview_timeseries(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        if 'report_date' in parameters:
            json_res = api_connection.exec_get_url('/api/dwh/productviewtimeseries/', parameters)
        else:
            json_res = api_connection.exec_get_url('/api/dwh/productviewtimeseries/latest/', parameters)

        logger.info(f"DWH json_res:{json_res}")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_flexibility_activations(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        if 'report_date' in parameters:
            json_res = api_connection.exec_get_url('/api/dwh/flexibilityactivations/', parameters)
        else:
            json_res = api_connection.exec_get_url('/api/dwh/flexibilityactivations/latest/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_hedgeview_timeseries(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/hedgeviewtimeseries/latest/', parameters)
        logger.info(f"DWH json_res:{json_res}")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_grid_exposure(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/gridexposure/latest/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_report_types(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/reporttypes/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_report_dates(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/reportdates/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_portfolios(api_connection: ApiConnection, parameters: dict={}):
        """Fetches  reports
        """
        json_res = api_connection.exec_get_url('/api/dwh/reportportfolios/', parameters)
        if json_res is None:
            return None
        return json_res