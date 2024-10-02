
import importlib

def dynamic_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
def contract_from_embedded_dictionary(d):
    contract_class = dynamic_import("energydeskapi.contracts.contracts_api.Contract")
    obj=contract_class()
    obj.external_contract_id=d['external_contract_id']
    obj.trading_book = d['trading_book']
    return obj

# external_contract_id = None,
# trading_book = None,
# contract_price = None,
# contract_qty = None,
# trading_fee = None,
# clearing_fee = None,
# trade_date = None,
# trade_datetime = None,
# commodity_type = None,
# instrument_type = None,
# contract_status = None,
# buy_or_sell = None,
# counterpart = None,
# market = None,
# trader = None,
# marketplace_product = None,
# delivery_type = DeliveryTypeEnum.FINANCIAL.value,
# profile_type = ProfileTypeEnum.BASELOAD.value,
# profile_category = ProfileTypeEnum.BASELOAD.name,
# quentity_type = QuantityTypeEnum.EFFECT.value,
# quantity_unit = QuantityUnitEnum.MW.value,
# contract_type = ContractTypeEnum.NASDAQ.value,
# asset_link = None