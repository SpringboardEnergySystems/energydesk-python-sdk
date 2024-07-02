import logging
import pandas as pd
from energydeskapi.sdk.common_utils import key_from_url
from energydeskapi.portfolios.portfolio_api import PortfoliosApi
logger = logging.getLogger(__name__)

class ReportParameter:
    def __init__(self):
        self.pk = 0
        self.parameter_code = None
        self.value_unit = None

    def get_dict(self):
        dict = {}
        dict['pk'] = self.pk
        if self.parameter_code is not None: dict['parameter_code'] = self.parameter_code
        if self.value_unit is not None: dict['value_unit'] = self.value_unit
        return dict

    @staticmethod
    def from_simple_dict(d):
        c=ReportParameter()
        c.pk=d['pk']
        c.parameter_code=d['parameter_code']
        c.value_unit = d['value_unit']
        return c
class ReportSetup:
    def __init__(self):
        self.pk = 0
        self.currency = None
        self.report_type = None
        self.resolution = None
        self.portfolio_id = None
        self.report_parameters=[]
    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.currency is not None: dict['currency'] = self.currency
        if self.report_type is not None: dict['report_type'] = self.report_type
        if self.resolution is not None: dict['resolution'] = self.resolution
        if self.portfolio_id is not None: dict['portfolio'] = PortfoliosApi.get_portfolio_url(api_conn, self.portfolio_id)
        dict['report_parameters']=[]
        for rp in self.report_parameters:
            dict['report_parameters'].append(rp.get_dict())
        return dict
    @staticmethod
    def from_simple_dict(d):
        c=ReportSetup()
        c.pk=d['pk']
        c.currency=d['parameter_code']
        c.report_type = d['report_type']
        c.resolution = d['resolution']
        c.portfolio_id = key_from_url(d['portfolio'])
        for rp in d['report_parameters']:
            c.report_parameters.append(rp.from_simple_dict())
        return c
class ReportSetupApi:
    """ Class for audit log REST API
    """

    @staticmethod
    def get_report_setups(api_connection, parameters={}):
        """Fetches all assets

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/reporting/reportsetup/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def upsert_report_setups(api_connection, report_setup):
        """Registers/Updates asset

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param asset: asset object
        :type asset: str, required
        """
        logger.info("Upserting report setup")
        if report_setup.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/reporting/reportsetup/' + str(report_setup.pk) + "/", report_setup.get_dict())
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/reporting/reportsetup/', report_setup.get_dict())
        return success, returned_data, status_code, error_msg