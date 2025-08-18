import logging

from energydeskapi.sdk.api_connection import ApiConnection

from energydeskapi.assets.assets_api import AssetsApi
import pandas as pd
from energydeskapi.grid.grid_api import GridNodeApi
from energydeskapi.contracts.contracts_api import ContractsApi
logger = logging.getLogger(__name__)



class CapacityTender:
    def __init__(self):
        self.pk = 0
        self.gridnode_asset = 0
        self.requested_profile={}
        self.quantity_requested=0
        self.quantity_type=0
        self.quantity_unit=0
        self.availability_price=0
        self.activation_price=0
        self.price_currency=0
        self.period_from=0
        self.period_until=0

    def get_dict(self, api_connection):
        dict = {}
        dict['pk'] = self.pk
        if self.gridnode_asset is not None: dict['gridnode_asset'] = GridNodeApi.get_grid_node_url(api_connection, self.gridnode_asset)
        if self.requested_profile is not None: dict['requested_profile'] = self.requested_profile
        if self.quantity_requested is not None: dict['quantity_requested'] = self.quantity_requested
        if self.quantity_unit is not None: dict['quantity_unit'] = ContractsApi.get_quantity_unit_url(api_connection,
                                                                                                            self.quantity_unit)
        if self.quantity_type is not None: dict['quantity_type'] = ContractsApi.get_quantity_type_url(api_connection,
                                                                                                            self.quantity_type)
        if self.availability_price is not None: dict['availability_price'] = self.availability_price
        if self.activation_price is not None: dict['activation_price'] = self.activation_price
        if self.price_currency is not None: dict['price_currency'] = self.price_currency
        if self.period_from is not None: dict['period_from'] = self.period_from
        if self.period_until is not None: dict['period_until'] = self.period_until
        return dict



class CapacityTenderApi:
    """ Class for assets

    """

    @staticmethod
    def upsert_capacity_tender(api_connection: ApiConnection, capacity_tender):

        logger.info("Upserting Capacity Tender")
        if capacity_tender.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/flexiblepower/capacitytender/' + str(capacity_tender.pk) + "/", capacity_tender.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/flexiblepower/capacitytender/', capacity_tender.get_dict(api_connection))
        return success, returned_data, status_code, error_msg

