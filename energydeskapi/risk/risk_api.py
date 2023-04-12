import logging
import pandas as pd
logger = logging.getLogger(__name__)

class RiskParameters:

    def __init__(self,pk=0,
                 risk_free_rate=None,
                 volatlity=None):
        self.risk_free_rate=risk_free_rate
        self.volatlity=volatlity
        self.pk=pk
    def get_dict(self,api_conn):
        dict = {}
        dict['pk'] = self.pk
        if self.risk_free_rate is not None:
            dict['risk_free_rate']=self.risk_free_rate
        if self.volatlity is not None:
            dict['volatility']=self.volatlity
        return dict
class RiskApi:
    """Class for risk

    """
    @staticmethod
    def upsert_global_risk_parameters(api_connection, risk_params):
        """Updates global risk parameters
        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        print(risk_params.get_dict(api_connection))
        if risk_params.pk>0:
            print("It is an existing configuration")
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url('/api/riskmanager/globalriskparameters/' + str(risk_params.pk) + "/",risk_params.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/globalriskparameters/',risk_params.get_dict(api_connection))
        return success, returned_data, status_code, error_msg
    @staticmethod
    def get_risk_parameters(api_connection, parameters={}):
        """Fetches credit ratings for counterparts

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching risk parameters")
        json_res = api_connection.exec_get_url('/api/riskmanager/globalriskparameters/', parameters)
        if json_res is not None:
            return json_res
        return None
    @staticmethod
    def calc_volatilities(api_connection, months_back, price_areas):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Calc Volatilities")
        payload={
            'months_back':months_back,
            'price_areas':price_areas
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/calcvolatilities/', payload)
        print(error_msg)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calc_volatilities_df(api_connection, months_back, price_areas):
        success, json_res, status_code, error_msg=RiskApi.calc_volatilities(api_connection, months_back, price_areas)
        if success ==False:
            return None
        df=pd.DataFrame(data=eval(json_res))
        return df

    @staticmethod
    def calc_covariance_var(api_connection, portfolio_id, days_back=40):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Calc Covariance Var")
        payload={
            'price_days':days_back,
            'portfolio_id':portfolio_id
        }
        print(payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/calccovariancevar/', payload)
        #print(error_msg)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calc_covariance_var_df(api_connection, trading_books=[], days_back=40):
        success, json_res, status_code, error_msg=RiskApi.calc_covariance_var(api_connection, trading_books, days_back)
        if success ==False:
            return None
        var_bins=json_res['var_bins']
        portfolio_mean = json_res['portfolio_mean']
        portfolio_stdev = json_res['portfolio_stdev']
        dfvars=pd.DataFrame(data=var_bins)
        #df=pd.DataFrame(data=eval(json_res))
        return dfvars,portfolio_mean,portfolio_stdev