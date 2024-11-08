from dataclasses import dataclass
from typing import Optional

from energydeskapi.types.contract_enum_types import QuantityTypeEnum


@dataclass(frozen=True)
class ContractForLiveViewMessage:
    trading_book_id: int
    ticker: str
    quantity: float
    volume: float
    contract_price: float
    quentity_type: str #QuantityTypeEnum
    buy_or_sell: str #"BUY" or "SELL"

@dataclass(frozen=True)
class ContractChangeMessage:
    contract: ContractForLiveViewMessage
    replaced_contract: Optional[ContractForLiveViewMessage]

