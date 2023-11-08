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
    def save_credit_rating(api_connection, company_regnumber, country="NO", credit_calc_parans=CreditCalculation()):
        qry_payload = credit_calc_parans.get_dict()
        qry_payload['country']=country
        qry_payload['company_regnumber'] = company_regnumber
        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/creditrisk/saverating/', qry_payload)
        return success, json_res, status_code, error_msg

    @staticmethod
    def get_ratings(api_connection, params={}):
        """Fetching list of companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching rated companies")
        json_res=api_connection.exec_get_url('/api/creditrisk/ratings/embedded/', params)
        if json_res is not None:
            return json_res
        return None

    # Only latest per company is retudned
    @staticmethod
    def get_distinct_ratings(api_connection, params={}):
        """Fetching list of companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching rated companies")
        json_res=api_connection.exec_get_url('/api/creditrisk/ratings/distinct/', params)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_accounts(api_connection, params={}):
        """Fetching list of companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching rated companies")
        json_res=api_connection.exec_get_url('/api/creditrisk/companyaccounts/', params)
        if json_res is not None:
            return json_res
        return None

class ManualCreditCalculation:
    def __init__(self, **payload):
        """
        company: ForeignKey to company object
        rating_datetime: datetime object
        rating_data: final_rating
        """
        self.__dict__ = dict(payload)

    def get_dict(self):
        return self.__dict__

class ManualCreditRiskApi:
    """Class for credit risk

    """
    @staticmethod
    def save_manual_credit_rating(api_connection, payload):
        try:
            company = payload['company']
            rating_datetime = payload['rating_datetime']
            rating_data = payload['rating_data']
        except:
            raise ValueError("Inappropriate values")
        manual_credit_params = ManualCreditCalculation(payload={
            'company': company,
            'rating_datetime': rating_datetime,
            'rating_data': rating_data
        })
        qry_payload = manual_credit_params.get_dict()
        print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/creditrisk/manualrating/', qry_payload)
        return success, json_res, status_code, error_msg
