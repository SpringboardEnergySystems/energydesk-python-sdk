from typing import Optional

from energydeskapi.contracts.contracts_api import Contract


class ContractChangeMessage:
    contract: Contract
    replaced_contract: Optional[Contract]
