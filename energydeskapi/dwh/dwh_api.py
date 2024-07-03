import logging
logger = logging.getLogger(__name__)


class DwhApi:
    """Class for user access to Datawarehouse
    """
    @staticmethod
    def get_contract_dimension(api_connection, parameters={}):
        """Fetches  contracts
        """
        json_res = api_connection.exec_get_url('/api/dwh/contracts/', parameters)
        if json_res is None:
            return None
        return json_res