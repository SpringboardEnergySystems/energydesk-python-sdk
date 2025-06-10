import logging
from typing import Dict, Union
import pandas as pd
import json
from json import JSONEncoder
from dataclasses import dataclass
from energydeskapi.assetdata.assetdata_api import DateTimeEncoder
from energydeskapi.portfolios.portfolio_api import PortfoliosApi
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from datetime import timezone, datetime, date
import pendulum
logger = logging.getLogger(__name__)

@dataclass
class RollingProduct:
    pk : int
    ticker : str
    original_ticker: str
    trading_date: datetime
    size: int
    currency: str
    denomination: str
    delivery_from: datetime
    delivery_until: datetime
    price: float
    prev_price: float
    log_returns: float
    market: str # URL
    commodity_type: str # URL


    @property
    def __dict__(self):
        """
        get a python dictionary
        """
        return asdict(self)



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
        logger.debug(f"Api connection: {risk_params.get_dict(api_connection)}")
        if risk_params.pk>0:
            logger.info("It is an existing configuration")
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
    def get_rolling_products(api_connection, params={})->dict:
        """Lists rolling products
        """
        logger.info("Loads rolling products")
        json_res = api_connection.exec_get_url('/api/markets/rollingproducts/',params)
        return json_res

    @staticmethod
    def get_rolling_products_embedded(api_connection, params={})->dict:
        """Lists rolling products
        """
        logger.info("Loads rolling products")
        json_res = api_connection.exec_get_url('/api/markets/rollingproducts/embedded/',params)
        return json_res

    @staticmethod
    def upsert_rolling_product(api_connection, product: RollingProduct):
        payload=product.__dict__
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/markets/rollingproducts/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def upsert_covariance_data(api_connection,  trading_date:pendulum,timestamp:pendulum, days_history:int,decay_factor:float, covariance_data: dict, correlation_data:dict):
        logger.info("Upserting covariance data product")
        payload = {
            'trading_date': str(trading_date)[:10],
            'timestamp': str(timestamp),
            'days_history': days_history,
            'decay_factor': decay_factor,
            'covariance_data': covariance_data,
            'correlation_data': correlation_data
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/varcovariances/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def upsert_productreturns_data(api_connection, trading_date:pendulum,timestamp:pendulum,days_history:int,decay_factor:float, returns_data: dict):
        logger.info("Upserting product returns")
        payload={
            'trading_date': str(trading_date)[:10],
            'timestamp': str(timestamp),
            'days_history':days_history,
            'decay_factor':decay_factor,
            'returns_data':returns_data
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/varproductreturns/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_product_returns(api_connection, params={})->dict:
        """Lists product returns
        """
        logger.info("Loads product returns")
        json_res = api_connection.exec_get_url('/api/riskmanager/varproductreturns/',params)
        return json_res


    @staticmethod
    def get_rolling_tickers(api_connection, params={})->dict:
        """Lists product returns
        """
        logger.info("Loads product returns tickers")
        json_res = api_connection.exec_get_url('/api/markets/rollingproducts/tickers/',params)
        return json_res

    @staticmethod
    def get_rolling_products_returns(api_connection, params={})->dict:
        """Lists product returns
        """
        logger.info("Loads product returns tickers")
        json_res = api_connection.exec_get_url('/api/riskmanager/rollingproductreturns/',params)
        return json_res


    @staticmethod
    def get_var_portfolios(api_connection, params={})->dict:
        """Lists VaR portfolios
        """
        logger.info("Loads current var portfolios")
        json_res = api_connection.exec_get_url('/api/riskmanager/varportfolios/',params)
        return json_res

    @staticmethod
    def get_product_returns_embedded(api_connection, params={})->dict:
        """Lists product returns
        """
        logger.info("Loads product returns")
        json_res = api_connection.exec_get_url('/api/riskmanager/varproductreturns/embedded/',params)
        return json_res


    @staticmethod
    def get_covariance_data(api_connection, params={})->dict:
        """Lists product returns
        """
        logger.info("Loads product returns")
        json_res = api_connection.exec_get_url('/api/riskmanager/varcovariances/',params)
        return json_res

    @staticmethod
    def get_covariance_data_embedded(api_connection, params={})->dict:
        """Lists product returns
        """
        logger.info("Loads product returns")
        json_res = api_connection.exec_get_url('/api/riskmanager/varcovariances/embedded/',params)
        return json_res

    @staticmethod
    def upsert_var_calculation(api_connection,  trading_date:pendulum,timestamp:pendulum, days_history:int,decay_factor:float,
                              portfolio_id:int, var95:float, var99:float, port_mean:float, port_stdev:float, var_data:dict):
        logger.info("Upserting VaR calculation")
        payload = {
            'trading_date': str(trading_date)[:10],
            'timestamp': str(timestamp),
            'days_history': days_history,
            'decay_factor': round(decay_factor,6),
            'portfolio': PortfoliosApi.get_portfolio_url(api_connection, portfolio_id),
            'var95': round(var95,6),'var99': round(var99,6),'portfolio_mean': round(port_mean,6),'portfolio_stddev': round(port_stdev,6),'var_data': var_data
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/varcalculations/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_var_calculations(api_connection, params={})->dict:
        """Lists VaR calculations
        """
        logger.info("Loads VaR calculations")
        json_res = api_connection.exec_get_url('/api/riskmanager/varcalculations/',params)
        return json_res
    @staticmethod
    def get_var_calculations_compact(api_connection, params={})->dict:
        """Lists VaR calculations
        """
        logger.info("Loads VaR calculations")
        json_res = api_connection.exec_get_url('/api/riskmanager/varcalculations/compact/',params)
        return json_res
    @staticmethod
    def get_var_calculations_embedded(api_connection, params={})->dict:
        """Lists VaR calculations
        """
        logger.info("Loads VaR calculations")
        json_res = api_connection.exec_get_url('/api/riskmanager/varcalculations/embedded/',params)
        return json_res
    @staticmethod
    def get_var_dates(api_connection, params={})->dict:
        """Lists VaR calculations
        """
        logger.info("Loads VaR dates in DB")
        json_res = api_connection.exec_get_url('/api/riskmanager/vardates/',params)
        return json_res
    @staticmethod
    def get_var_portfolios_calculated(api_connection, params={})->dict:
        """Lists VaR portfolios that have been calculated. May filter on date
        """
        logger.info("Loads VaR portfolios in DB")
        json_res = api_connection.exec_get_url('/api/riskmanager/varportfolioscalculated/',params)
        return json_res

    @staticmethod
    def post_marketestimators(api_connection, payload):
        """posts market estimators to database"""
        logger.info("Posting market estimators")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/marketestimators/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_marketestimators(api_connection):
        """Fetches market estimators from the database"""
        logger.info("Fetching market estimators")
        json_res = api_connection.exec_get_url('/api/riskmanager/marketestimators/')
        return json_res

    @staticmethod
    def get_marketestimators_latest(api_connection):
        """Fetches market estimators from the database"""
        logger.info("Fetching market estimators")
        json_res = api_connection.exec_get_url('/api/riskmanager/marketestimators/latest/')
        return json_res

    @staticmethod
    def get_marketestimators_dict(api_connection, latest=True) -> Dict[str, pd.DataFrame | list] | None:
        """Fetches market estimators from the database"""
        logger.info("Fetching market estimators")
        if latest:
            url = '/api/riskmanager/marketestimators/latest/'
        else:
            url = '/api/riskmanager/marketestimators/'
        json_res = api_connection.exec_get_url(url)

        record = json_res[0] if isinstance(json_res, list) and len(json_res) > 0 else json_res
        if not record:
            return None
        # Retrieve the stored fields. They are assumed to be JSON-encoded strings.
        corr_str = record.get("correlation_data")
        discount_str = record.get("discount_factor_data")
        column_order = record.get("column_order")
        estimator_id = record.get("id")
        data = {}
        # Convert JSON strings to Python objects (lists)
        if corr_str and discount_str and column_order and estimator_id:
            data['id'] = estimator_id
            try:
                correlation_list = json.loads(corr_str) if isinstance(corr_str, str) else corr_str
            except Exception as e:
                logger.error(f"Error decoding correlation_data: {e}")
                correlation_list = []
            df_correlation = pd.DataFrame(correlation_list)
            if len(column_order) == df_correlation.shape[0] == df_correlation.shape[1]:
                df_correlation.columns = column_order
                df_correlation.index = column_order
            else:
                logger.error("Column order does not match the correlation matrix dimensions")
                return None
            data['correlation'] = df_correlation
            try:
                discount_list = json.loads(discount_str) if isinstance(discount_str, str) else discount_str
            except Exception as e:
                logger.error(f"Error decoding discount_factor: {e}")
                discount_list = []
            discount = list(discount_list)
            data['discount_factor'] = discount
            return data
        return None

    @staticmethod
    def get_create_report(api_connection, payload):
        """updates or creates a simprice report"""
        logger.info("Posting simprice report")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/simpricereportdata/', payload)
        return success, json_res, status_code, error_msg


    @staticmethod
    def get_market_areas(api_connection):
        """Fetches market areas from the database"""
        logger.info("Fetching market areas")
        json_res = api_connection.exec_get_url('/api/riskmanager/marketareas/')
        return json_res

    @staticmethod
    def get_market_areas_filtered(api_connection, areas:list[str]):
        """Fetches market areas from the database"""
        logger.info("Fetching market areas")
        json_res = api_connection.exec_get_url('/api/riskmanager/marketareas/', {'name__in': areas})
        return json_res

    @staticmethod
    def post_market_area(api_connection, payload):
        """posts market areas to database"""
        logger.info("Posting market areas")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/marketareas/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def bulk_post_market_areas(api_connection, payload):
        """posts market areas to database"""
        logger.info("Bulk posting market areas")
        # The endpoint for bulk insertion is appended with the action's name 'bulk_create'
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/marketareas/bulk_create/', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def post_batch_simulation(api_connection, payload):
        """posts batch simulation to database"""
        logger.info("Posting batch simulation")
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/riskmanager/simpricebatch', payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_simulation_batches(api_connection, report_id, page=1, page_size=1):
        """Fetches a page of simulation batches for a given simulation report id"""
        logger.info(f"Fetching simulation batches for report id: {report_id}, page: {page}, page_size: {page_size}")
        params = {
            'report': report_id,
            'page': page,
            'page_size': page_size
        }
        json_res = api_connection.exec_get_url('/api/riskmanager/simpricebatch/', params)
        return json_res
