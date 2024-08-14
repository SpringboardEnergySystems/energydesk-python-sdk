from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from dataclasses import dataclass

import json


from datetime import datetime
from energydeskapi.creditrisk.dataclasses.dataclasses_utils import DataclassEncoder, date_hook

@dataclass
class CompanyAccounts:
    company_name: str
    company_regnumber: str
    nace_industry_code: str
    accounts: dict
    country: str
    financial_data_type: str

    @property
    def json(self):
        """
        get the json formated string
        """
        return json.dumps(self.__dict__, cls=DataclassEncoder)
    @property
    def json_dict(self):
        return json.loads(json.dumps(self.__dict__,cls=DataclassEncoder))
    @staticmethod
    def from_json(elem):
        """
        get the json formated string
        """
        json_obj = json.loads(elem)#,object_hook=date_hook)
        mpobj = CompanyAccounts(**json_obj)
        return mpobj
