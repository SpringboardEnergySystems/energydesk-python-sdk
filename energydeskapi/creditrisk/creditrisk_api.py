import logging
import pandas as pd


logger = logging.getLogger(__name__)


#  Change
class CreditRiskApi:
    """Class for credit risk

    """
    @staticmethod
    def get_capstructure_url(api_connection, pk):
        return api_connection.get_base_url() + '/api/creditrisk/ratings/capstructure/' + str(pk) + "/"
    @staticmethod
    def get_capstructure(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/creditrisk/ratings/capstructure/', parameters)
        return json_res
    @staticmethod
    def get_capstructure_df(api_connection, parameters={}):
        json_res = CreditRiskApi.get_capstructure(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_liquidity_url(api_connection, pk):
        return api_connection.get_base_url() + '/api/creditrisk/ratings/liquidity/' + str(pk) + "/"
    @staticmethod
    def get_liquidity(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/creditrisk/ratings/liquidity/', parameters)
        return json_res
    @staticmethod
    def get_liquidity_df(api_connection, parameters={}):
        json_res = CreditRiskApi.get_liquidity(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df


    @staticmethod
    def get_diversification_url(api_connection, pk):
        return api_connection.get_base_url() + '/api/creditrisk/ratings/diversification/' + str(pk) + "/"
    @staticmethod
    def get_diversification(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/creditrisk/ratings/diversification/', parameters)
        return json_res
    @staticmethod
    def get_diversification_df(api_connection, parameters={}):
        json_res = CreditRiskApi.get_diversification(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df



    @staticmethod
    def get_comparableratings_url(api_connection, pk):
        return api_connection.get_base_url() + '/api/creditrisk/ratings/comparableratings/' + str(pk) + "/"
    @staticmethod
    def get_comparableratings(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/creditrisk/ratings/comparableratings/', parameters)
        return json_res
    @staticmethod
    def get_comparableratings_df(api_connection, parameters={}):
        json_res = CreditRiskApi.get_comparableratings(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df



    @staticmethod
    def get_governance_url(api_connection, pk):
        return api_connection.get_base_url() + '/api/creditrisk/ratings/governance/' + str(pk) + "/"
    @staticmethod
    def get_governance(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/creditrisk/ratings/governance/', parameters)
        return json_res
    @staticmethod
    def get_governance_df(api_connection, parameters={}):
        json_res = CreditRiskApi.get_governance(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df


    @staticmethod
    def get_govinfluence_url(api_connection, pk):
        return api_connection.get_base_url() + '/api/creditrisk/ratings/govinfluence/' + str(pk) + "/"
    @staticmethod
    def get_govinfluence(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/creditrisk/ratings/govinfluence/', parameters)
        return json_res
    @staticmethod
    def get_govinfluence_df(api_connection, parameters={}):
        json_res = CreditRiskApi.get_govinfluence(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df


    @staticmethod
    def get_financialpos_url(api_connection, pk):
        return api_connection.get_base_url() + '/api/creditrisk/ratings/financialpos/' + str(pk) + "/"
    @staticmethod
    def get_financialpos(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/creditrisk/ratings/financialpos/', parameters)
        return json_res
    @staticmethod
    def get_financialpos_df(api_connection, parameters={}):
        json_res = CreditRiskApi.get_financialpos(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_competivepos_url(api_connection, pk):
        return api_connection.get_base_url() + '/api/creditrisk/ratings/competivepos/' + str(pk) + "/"
    @staticmethod
    def get_competivepos(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/creditrisk/ratings/competivepos/', parameters)
        return json_res
    @staticmethod
    def get_competivepos_df(api_connection, parameters={}):
        json_res = CreditRiskApi.get_competivepos(api_connection, parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df
