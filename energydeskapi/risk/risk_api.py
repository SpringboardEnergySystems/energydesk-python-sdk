import logging
import pandas as pd
import json
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
        logger.debug(f"Calc volatilities error {error_msg}")
        return success, json_res, status_code, error_msg

    @staticmethod
    def calc_volatilities_df(api_connection, months_back, price_areas):
        success, json_res, status_code, error_msg=RiskApi.calc_volatilities(api_connection, months_back, price_areas)
        if success ==False:
            return None
        df=pd.DataFrame(data=eval(json_res))
        return df

    @staticmethod
    def calc_covariance_var(api_connection, portfolio_id, days_back=40, decay_factor=0.94):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={
            'price_days':days_back,
            'decay_factor': decay_factor,
            'portfolio_id':portfolio_id
        }
        logger.info(f"Calc Covariance Var with {payload}")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/calccovariancevar/', payload)
        #print(error_msg)
        return success, json_res, status_code, error_msg

    @staticmethod
    def calc_covariance_var_df(api_connection, portfolio_id, days_back=40, decay_factor=0.94):
        success, json_res, status_code, error_msg=RiskApi.calc_covariance_var(api_connection, portfolio_id, days_back, decay_factor)
        if success ==False:
            logger.error(f"Covariance calculation gave error: {error_msg}")
            return None,None,None
        var_bins=json_res['var_bins']
        portfolio_mean = json_res['portfolio_mean']
        portfolio_stdev = json_res['portfolio_stdev']
        dfvars=pd.DataFrame(data=var_bins)
        #df=pd.DataFrame(data=eval(json_res))
        return dfvars,portfolio_mean,portfolio_stdev

    @staticmethod
    def calc_covariance_matrix(api_connection, days_back=40, decay_factor=0.94):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload={
            'price_days':days_back,
            'decay_factor': decay_factor,
        }
        logger.info(f"Calc Covariance Matrix with payload {payload}")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/calccovariancematrix/', payload)
        #print(error_msg)
        return success, json_res, status_code, error_msg


    @staticmethod
    def calc_covariance_matrix_df(api_connection, days_back=40, decay_factor=0.94):
        success, json_res, status_code, error_msg=RiskApi.calc_covariance_matrix(api_connection,  days_back, decay_factor)
        if success ==False:
            logger.error(f"Calculating the convariance matrix got:{error_msg}")
            return None,None,None
        dfvars=pd.DataFrame(data=json.loads(json_res['covariance_data']))
        dfvars.index=dfvars.columns.to_flat_index()
        return dfvars

    @staticmethod
    def get_rolling_products(api_connection, price_days=40, ticker=None):
        """Lists the types of commodities

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Loads rolling products")
        params={'price_days':price_days}
        if ticker is not None:
            params['ticker__icontains'] = ticker
        print('get_rolling_products params:', params)
        json_res = api_connection.exec_get_url('/api/riskmanager/rollingproducts/',params)
        return json_res

    @staticmethod
    def post_marketestimators(api_connection, payload):
        """posts market estimators to database"""
        logger.info("Posting market estimators")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/markestimators/', payload)
        return success, json_res, status_code, error_msg
    
    @staticmethod
    def get_marketestimators(api_connection):
        """Fetches market estimators from the database"""
        logger.info("Fetching market estimators")
        json_res = api_connection.exec_get_url('/api/riskmanager/markestimators/')
        return json_res
    
    @staticmethod
    def get_marketestimators_dict(api_connection):
        """Fetches market estimators from the database"""
        logger.info("Fetching market estimators")
        json_res = api_connection.exec_get_url('/api/riskmanager/markestimators/')
        
        record = json_res[0] if json_res else {}
        # Retrieve the stored fields. They are assumed to be JSON-encoded strings.
        vol_str = record.get("volatility_data")
        corr_str = record.get("correlation_data")
        
        # Convert JSON strings to Python objects (lists) if needed.
        try:
            volatility_list = json.loads(vol_str) if isinstance(vol_str, str) else vol_str
        except Exception as e:
            print(f"Error decoding volatility_data: {e}")
            volatility_list = []
            
        try:
            correlation_list = json.loads(corr_str) if isinstance(corr_str, str) else corr_str
        except Exception as e:
            print(f"Error decoding correlation_data: {e}")
            correlation_list = []
        
        # Since discount_factor is not stored in the model, we create an empty list.
        discount_factor_list = []
        
        # Convert the lists to pandas DataFrames.
        df_volatility = pd.DataFrame(volatility_list)
        df_correlation = pd.DataFrame(correlation_list)
        df_discount_factor = pd.DataFrame(discount_factor_list)
        
        # Build the output dictionary in the same format as load_dummy_data_from_json.
        data = {
            'volatility': df_volatility,
            'correlation': df_correlation,
            'discount_factor': df_discount_factor,
        }
        
        print("Data retrieved and converted to DataFrames successfully!")
        return data