
from importlib import import_module

def dynamic_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
def contract_from_embedded_dictionary(d):
    cls = getattr(import_module('energydeskapi.contracts.contracts_api'), 'Contract')
    obj=cls()
    obj.pk=d['pk']
    obj.external_contract_id=d['external_contract_id']
    obj.trading_book = d['trading_book']['pk']
    obj.contract_price = d['contract_price']
    obj.contract_qty = d['quantity']
    obj.trading_fee = d['trading_fee']['amount']
    obj.clearing_fee = d['clearing_fee']['amount']
    obj.trade_date = d['trade_date']
    obj.trade_datetime = d['trade_time']
    obj.commodity_type = d['commodity']['commodity_type']['pk']
    obj.instrument_type = d['commodity']['instrument_type']['pk']
    obj.contract_status = d['contract_status']['pk']
    obj.buy_or_sell = d['buy_or_sell']
    obj.counterpart = d['counterpart']['pk']
    obj.market = d['commodity']['market']['pk']
    obj.trader = d['trader']['pk']
    obj.marketplace_product = d['commodity']['product_code']
    obj.delivery_type = d['commodity']['delivery_type']
    obj.profile_type = d['commodity']['profile_type']
    obj.profile_category = d['commodity']['profile_category']
    obj.quantity_type = d['quantity_type']['pk']
    obj.quantity_unit = d['quantity_unit']['pk']
    obj.contract_type = d['contract_type']['pk']
    obj.asset_link = d['commodity']['asset_link']
    obj.area= d['commodity']['area']
    return obj

