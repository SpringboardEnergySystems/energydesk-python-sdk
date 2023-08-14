import logging
import pandas as pd
from energydeskapi.types.creditrisk_enum_types import DiversificationEnums,FinancialPolicyEnums,\
LiquidityEnums, ComparableRatingsEnums,ManagmentGovernanceEnums,CapStructEnums,GovernmentInfluenceEnums, \
CompetitivePosEnums


logger = logging.getLogger(__name__)

class CreditCalculation:
    def __init__(self):
        self.government_influence_adjust = GovernmentInfluenceEnums.MODERATE.value
        self.diversification = DiversificationEnums.NEUTRAL.value
        self.capital_structure = CapStructEnums.NEUTRAL.value
        self.liquidity = LiquidityEnums.ADEQUATE.value
        self.financial_policy = FinancialPolicyEnums.NEUTRAL.value
        self.management_governance = ManagmentGovernanceEnums.SATISFACTORY.value
        self.comparable_rating_analysis = ComparableRatingsEnums.NEUTRAL.value
        self.competitive_advantage =  CompetitivePosEnums.ADEQUATE.value
        self.scale_scope_diversity = CompetitivePosEnums.ADEQUATE.value
        self.operating_efficiency = CompetitivePosEnums.ADEQUATE.value


    def get_dict(self):
        dict = {}
        if self.government_influence_adjust is not None: dict['government_influence_adjust'] = self.government_influence_adjust
        if self.diversification is not None: dict['diversification'] = self.diversification
        if self.capital_structure is not None: dict['capital_structure'] = self.capital_structure
        if self.liquidity is not None: dict['liquidity'] = self.liquidity
        if self.financial_policy is not None: dict['financial_policy'] = self.financial_policy
        if self.management_governance is not None: dict['management_governance'] = self.management_governance
        if self.comparable_rating_analysis is not None: dict['comparable_rating_analysis'] = self.comparable_rating_analysis
        if self.competitive_advantage is not None: dict['competitive_advantage'] = self.competitive_advantage
        if self.scale_scope_diversity is not None: dict['scale_scope_diversity'] = self.scale_scope_diversity
        if self.operating_efficiency is not None: dict['operating_efficiency'] = self.operating_efficiency
        return dict
#  Change
class CreditRiskApi:
    """Class for credit risk

    """

    @staticmethod
    def calculate_credit_rating(api_connection, company_regnumber, country="NO", credit_calc_parans=CreditCalculation()):
        qry_payload = credit_calc_parans.get_dict()
        qry_payload['country']=country
        qry_payload['company_regnumber'] = company_regnumber
        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/creditrisk/calculaterating/', qry_payload)
        return success, json_res, status_code, error_msg

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
