
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
    obj.contract_price = d['contract_price']
    obj.contract_qty = d['contract_qty']
    obj.trading_fee = d['trading_fee']
    obj.trade_date = d['trade_date']
    obj.trade_datetime = d['trade_datetime']
    obj.commodity_type = d['commodity_type']
    obj.instrument_type = d['instrument_type']
    obj.contract_status = d['contract_status']
    obj.buy_or_sell = d['buy_or_sell']
    obj.counterpart = d['counterpart']
    obj.market = d['market']
    obj.trader = d['trader']
    obj.marketplace_product = d['marketplace_product']
    obj.delivery_type = d['delivery_type']
    obj.profile_type = d['profile_type']
    obj.profile_category = d['profile_category']
    obj.quentity_type = d['quentity_type']
    obj.quantity_unit = d['quantity_unit']
    obj.contract_type = d['contract_type']
    obj.asset_link = d['asset_link']
    obj.area= d['area']
    return obj

