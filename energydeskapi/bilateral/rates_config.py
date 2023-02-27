from dataclasses import dataclass, asdict, fields, is_dataclass
from typing import List
from types import GenericAlias
import json
from dataclasses import dataclass, field
from itertools import count
from datetime import datetime
from uuid import uuid4
import json
import pytz
from dateutil import parser
from datetime import timezone, datetime



@dataclass
class RatesConfig:
    wacc: float
    discount_factor:float
    inflation: float = 0  # Used for industrial bilateral contracts
    company_tax_rate: float = 0.22
    land_value_tax_rate: float = 0.4501
    high_price_tax_rate: float = 0.23
    high_price_tax_trigger: float = 700  # NOK/MWh
    high_price_tax_start_date: datetime =  datetime(2022, 1, 1, 0, 0, 0, 0, tzinfo= pytz.timezone("Europe/Oslo"))
    high_price_tax_end_date: datetime = datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo= pytz.timezone("Europe/Oslo"))
