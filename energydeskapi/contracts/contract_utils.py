
from importlib import import_module

def dynamic_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def contract_from_embedded_dictionary(dct: dict):
    cls = getattr(import_module('energydeskapi.contracts.contracts_api'), 'Contract')
    obj = cls()
    obj.pk=dct['pk']
    obj.external_contract_id=dct['external_contract_id']
    obj.trading_book = dct['trading_book']['pk']
    obj.contract_price = dct['contract_price']
    obj.contract_qty = dct['quantity']
    obj.trading_fee = dct['trading_fee']['amount']
    obj.clearing_fee = dct['clearing_fee']['amount']
    obj.trade_date = dct['trade_date']
    obj.trade_datetime = dct['trade_time']
    obj.commodity_type = dct['commodity']['commodity_type']['pk']
    obj.instrument_type = dct['commodity']['instrument_type']['pk']
    obj.contract_status = dct['contract_status']['pk']
    obj.buy_or_sell = dct['buy_or_sell']
    obj.counterpart = dct['counterpart']['pk']
    obj.market = dct['commodity']['market']['pk']
    obj.trader = dct['trader']['pk']
    obj.marketplace_product = dct['commodity']['product_code']
    obj.delivery_type = dct['commodity']['delivery_type']
    obj.profile_type = dct['commodity']['profile_type']
    obj.profile_category = dct['commodity']['profile_category']
    obj.quantity_type = dct['quantity_type']['pk']
    obj.quantity_unit = dct['quantity_unit']['pk']
    obj.contract_type = dct['contract_type']['pk']
    obj.asset_link = dct['commodity']['asset_link']
    obj.area= dct['commodity']['area']
    return obj


def contract_cleared_message_from_embedded_dictionary(dct: dict):
    cls = getattr(import_module('energydeskapi.contracts.contract_messages'), 'ContractClearedMessage')
    obj = cls()
    obj.contract = contract_from_embedded_dictionary(dct['contract'])
    obj.replaced_contract = contract_from_embedded_dictionary(dct['replaced_contract']) if 'replaced_contract' in dct else None
    return obj
