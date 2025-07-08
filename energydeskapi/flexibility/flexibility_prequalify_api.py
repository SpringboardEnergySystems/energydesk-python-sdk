import json
import logging
import pendulum
from dataclasses import asdict
from dataclasses import dataclass

from energydeskapi.flexibility.datatypes.json_encoder import DateTimeEncoder

logger = logging.getLogger(__name__)



@dataclass(frozen=True)
class FlexMarketOffer:
    pk: int
    external_id: str # URL
    description: str  # URL
    seller_name: str # URL
    grid_node_name: str # URL
    period_from:str
    period_until:str
    availability_price:float
    offered_flexibility: dict
    @property
    def __dict__(self):
        """
        get a python dictionary
        """
        return asdict(self)
    @property
    def json(self):
        """
        get the json formated string
        """
        return json.dumps(self.__dict__, cls=DateTimeEncoder)


@dataclass(frozen=True)
class FlexPrequalBidTest:
    pk: int
    prequalification: str # URL
    offered_profile: dict
    offered_capacity_mw: float
    sample_portfolio_meterdata: dict
    @property
    def __dict__(self):
        """
        get a python dictionary
        """
        return asdict(self)
    @property
    def json(self):
        """
        get the json formated string
        """
        return json.dumps(self.__dict__, cls=DateTimeEncoder)





class FlexibilityPrequalifyApi:
    """ Class for flexibility and prequalification
    """


    @staticmethod
    def get_flex_prequalification_url(api_connection, order_status):
        status_pk = order_status if isinstance(order_status, int) else order_status.value
        return api_connection.get_base_url() + '/api/flexibility/prequalification/requests/' + str(status_pk) + "/"

    @staticmethod
    def get_prequal_bidquality(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexibility/prequalification/bidqualitytest/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_prequal_bidquality_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexibility/prequalification/bidqualitytest/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_prequal_requests_embedded(api_connection,  parameters={}):
        json_res = api_connection.exec_get_url('/api/flexibility/prequalification/requests/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_offers(api_connection, data: FlexMarketOffer):
        logger.debug("Upserting flex offer ")
        payload = json.loads(data.json)
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexibility/prequalification/productoffers/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def process_offer(api_conn, product_offer_id):
        payload = {'product_offer_id': product_offer_id }
        success, returned_data, status_code, error_msg = api_conn.exec_post_url(
            '/api/flexibility/prequalification/processoffer/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def buy_prequalified_offers(api_conn):
        payload = {}
        success, returned_data, status_code, error_msg = api_conn.exec_post_url(
            '/api/flexibility/prequalification/buyprequalifiedoffers/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def upsert_prequal_bidquality(api_connection, data: FlexPrequalBidTest):
        logger.debug("Upserting flex prequalif")
        payload = json.loads(data.json)

        if data.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexibility/prequalification/bidqualitytest/' + str(data.pk) + "/", payload)
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexibility/prequalification/bidqualitytest/', payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def make_prequalification_request(api_connection, longflex_offer_id,asset_id_list=['GUID1','GUID2','GUID3']):
        payload={'longflex_offer_id':longflex_offer_id,
               'requested_date_for_activationtest':str(pendulum.today(tz="Europe/Oslo")),
               'asset_list':asset_id_list}
        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexibility/prequalification/requestlongflexqualification/', payload)
        return success, returned_data, status_code, error_msg


