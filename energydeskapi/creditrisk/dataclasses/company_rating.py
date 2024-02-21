from dataclasses import dataclass, field
import json
from energydeskapi.creditrisk.dataclasses.company_accounts import CompanyAccounts
from datetime import datetime
from energydeskapi.creditrisk.dataclasses.dataclasses_utils import DataclassEncoder, date_hook
import pandas as pd

@dataclass
class FinancialStatement:
    ebitda: float
    revenue: float
    ffo: float
    debt_adj: float
    debt_ebitda: float
    ffo_debt: float
    weighting: list
    weighted_ebitda: float
    weighted_ffo: float
    weighted_debt: float
    weighted_debt_ebitda: float
    weighted_ffo_debt : float
    @property
    def json(self):
        return json.dumps(self.__dict__,cls=DataclassEncoder)
    @property
    def json_dict(self):
        return json.loads(json.dumps(self.__dict__,cls=DataclassEncoder))
    @staticmethod
    def from_json(elem):
        json_obj = json.loads(elem)
        mpobj = FinancialStatement(**json_obj)
        return mpobj



@dataclass
class Competitiveness:
    ebitdamargin_avg: float
    volatility_of_prob: int
    competitive_position: int
    @property
    def json(self):
        return json.dumps(self.__dict__,cls=DataclassEncoder)
    @property
    def json_dict(self):
        return json.loads(json.dumps(self.__dict__,cls=DataclassEncoder))
    @staticmethod
    def from_json(elem):
        json_obj = json.loads(elem)
        mpobj = Competitiveness(**json_obj)
        return mpobj


@dataclass
class CompanyRating:
    company_accounts: CompanyAccounts
    financial_statement: FinancialStatement
    competitiveness: Competitiveness
    cicra:float
    business_risk_profile:float
    financial_risk_profile: int
    anchor_rating: str
    standalone_cp: str
    final_rating: list
    rating_cat: int
    rating_datetime: datetime
    @property
    def json(self):
        return json.dumps(self.__dict__,cls=DataclassEncoder)
    @property
    def json_dict(self):
        return json.loads(json.dumps(self.__dict__,cls=DataclassEncoder))
    @staticmethod
    def from_json(elem):
        json_obj = json.loads(elem)
        mpobj = CompanyRating(**json_obj,object_hook=date_hook)
        return mpobj

@dataclass
class FinancialCompanyParams:
    currency: str
    total_operating_revenue: float
    commodity_diversity: float
    geographic_diversity: float
    avg_roc: float
    ser_ebitda_percentage:float 
    trading_risk_management:float
    ebitda: float
    ffo: float
    total_debt: float
    ffo_debt:float
    debt_ebitda:float

    @property
    def json(self):
        return json.dumps(self.__dict__,cls=DataclassEncoder)
    @property
    def json_dict(self):
        return json.loads(json.dumps(self.__dict__,cls=DataclassEncoder))
    @staticmethod
    def from_json(elem):
        json_obj = json.loads(elem)
        mpobj = FinancialStatement(**json_obj)
        return mpobj


@dataclass
class FinancialCompanyRating:
    company_accounts: CompanyAccounts
    financial_statement: FinancialCompanyParams
    cicra:float
    business_risk_profile:float
    financial_leverage: int
    anchor_rating: str
    standalone_cp: str
    final_rating: list
    rating_cat: int
    rating_datetime: datetime
    @property
    def json(self):
        return json.dumps(self.__dict__,cls=DataclassEncoder)
    @property
    def json_dict(self):
        return json.loads(json.dumps(self.__dict__,cls=DataclassEncoder))
    @staticmethod
    def from_json(elem):
        json_obj = json.loads(elem)
        mpobj = CompanyRating(**json_obj,object_hook=date_hook)
        return mpobj