import logging
logger = logging.getLogger(__name__)


class MarketsApi:
    """Class for markets

    """

    @staticmethod
    def get_market_url(api_connection, market_enum):
        """Fetches url for market from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param market_enum: market
        :type market_enum: str, required
        """
        return api_connection.get_base_url() +'/api/markets/markets/' + str(market_enum.value) + "/"
    @staticmethod
    def get_market_obj(api_connection, market_enum):
        """Fetches all markets objects with URL relations. Will only return markets for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/markets/' + str(market_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_instrument_type_url(api_connection, instrument_type_enum):
        """Fetches url for instrument type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param instrument_type_enum: type of instrument
        :type instrument_type_enum: str, required
        """
        return api_connection.get_base_url() +'/api/markets/instrumenttypes/' + str(instrument_type_enum.value) + "/"
    @staticmethod
    def get_instrument_type_obj(api_connection, instrument_type_enum):
        """Fetches all instrument type objects with URL relations. Will only return instrument types for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param instrument_type_enum: type of instrument
        :type instrument_type_enum: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/instrumenttypes/' + str(instrument_type_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_delivery_type_url(api_connection, delivery_type_enum):
        """Fetches url for commodity type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param delivery_type_enum: type of commodity
        :type delivery_type_enum: str, required
        """
        deltype = delivery_type_enum if isinstance(delivery_type_enum, int) else delivery_type_enum.value
        return api_connection.get_base_url() +'/api/markets/deliverytypes/' + str(deltype) + "/"

    @staticmethod
    def get_delivery_type_obj(api_connection, delivery_type_enum):
        """Fetches all commodity type objects with URL relations. Will only return commodity types for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodity_type_enum: type of commodity
        :type commodity_type_enum: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/deliverytypes/' + str(delivery_type_enum.value) + "/")
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_commodity_type_url(api_connection, commodity_type_enum):
        """Fetches url for commodity type from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodity_type_enum: type of commodity
        :type commodity_type_enum: str, required
        """
        comm_type = commodity_type_enum if isinstance(commodity_type_enum, int) else commodity_type_enum.value
        return api_connection.get_base_url() +'/api/markets/commoditytypes/' + str(comm_type) + "/"

    @staticmethod
    def get_commodity_type_obj(api_connection, commodity_type_enum):
        """Fetches all commodity type objects with URL relations. Will only return commodity types for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param commodity_type_enum: type of commodity
        :type commodity_type_enum: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/commoditytypes/' + str(commodity_type_enum.value) + "/")
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_commodity_types(api_connection, parameters={}):
        """Fetches all commodity types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/commoditytypes/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_commodity(api_connection, parameters={}):
        """Fetches all commodity types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/commoditydefinitions/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_instrument_types(api_connection, parameters={}):
        """Fetches all commodity types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/instrumenttypes/', parameters)
        if json_res is None:
            return None
        return json_res


    @staticmethod
    def get_blocksize_category_url(api_connection, blocksize_category_enum):
        """Fetches blocksize category from url

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param blocksize_category_enum: category of blocksize
        :type blocksize_category_enum: str, required
        """
        return api_connection.get_base_url() +'/api/markets/blocksizecategories/' + str(blocksize_category_enum.value) + "/"

    @staticmethod
    def get_blocksize_category_obj(api_connection, blocksize_category_enum):
        """Fetches all blocksize category objects with URL relations. Will only return blocksize categories for which the user has rights

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param blocksize_category_enum: category of blocksize
        :type blocksize_category_enum: str, required
        """

        json_res=api_connection.exec_get_url('/api/markets/blocksizecategories/' + str(blocksize_category_enum.value) + "/")
        if json_res is None:
            return None
        return json_res
