from dataclasses import dataclass
from typing import Optional

from energydeskapi.types.contract_enum_types import QuantityTypeEnum
@dataclass(frozen=True)
class PriceWithCurrency:
    amount: float
    currency: str

@dataclass(frozen=True)
class ContractForLiveViewMessage:
    id: int
    trading_book_id: int
    ticker: str
    market: str
    area: str
    instrument_type: str
    delivery_from: str
    delivery_until: str
    contract_type: str
    hours: int
    quantity: float
    volume: float
    contract_price: PriceWithCurrency
    quentity_type: str #QuantityTypeEnum
    buy_or_sell: str #"BUY" or "SELL"
    price_at_contract_creation: float

@dataclass(frozen=True)
class ContractChangeMessage:
    contract: ContractForLiveViewMessage
    replaced_contract: Optional[ContractForLiveViewMessage]

