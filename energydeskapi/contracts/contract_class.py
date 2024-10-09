import logging
import pandas as pd
from energydeskapi.sdk.common_utils import parse_enum_type,convert_loc_datetime_to_utcstr
from energydeskapi.sdk.money_utils import gen_json_money, gen_money_from_json
from energydeskapi.types.market_enum_types import DeliveryTypeEnum, ProfileTypeEnum
from energydeskapi.portfolios.tradingbooks_api import TradingBooksApi
from energydeskapi.marketdata.markets_api import MarketsApi
from energydeskapi.assets.assets_api import AssetsApi
from energydeskapi.marketdata.products_api import ProductHelper
from energydeskapi.customers.customers_api import CustomersApi
from energydeskapi.types.contract_enum_types import QuantityTypeEnum,QuantityUnitEnum, ContractTypeEnum
from energydeskapi.customers.users_api import UsersApi
from energydeskapi.sdk.common_utils import check_fix_date2str


logger = logging.getLogger(__name__)



class Contract:
    """ Class for contracts

    """
    def __init__(self,
                 external_contract_id=None,
                 trading_book=None,
                 contract_price=None,
                 contract_qty=None,
                 trading_fee=None,
                 clearing_fee=None,
                 trade_date=None,
                 trade_datetime=None,
                 commodity_type=None,
                 instrument_type=None,
                 contract_status=None,
                 buy_or_sell=None,
                 counterpart=None,
                 market=None,
                 trader=None,
                 marketplace_product=None,
                 delivery_type=DeliveryTypeEnum.FINANCIAL.value,
                 profile_type=ProfileTypeEnum.BASELOAD.value,
                 profile_category=ProfileTypeEnum.BASELOAD.name,
                 quentity_type=QuantityTypeEnum.EFFECT.value,
                 quantity_unit=QuantityUnitEnum.MW.value,
                 contract_type=ContractTypeEnum.NASDAQ.value,
                 asset_link=None
                 ):
        self.pk=0
        self.external_contract_id=external_contract_id
        self.contract_type=contract_type
        self.trading_book=trading_book
        self.contract_price=contract_price
        self.quantity = contract_qty
        self.trading_fee=trading_fee
        self.clearing_fee=clearing_fee
        self.trade_date=trade_date
        self.trade_datetime=trade_datetime
        self.quantity_unit=quantity_unit
        self.quantity_type=quentity_type
        self.commodity_type=commodity_type
        self.asset_link = asset_link
        self.profile_type=profile_type
        self.profile_category=profile_category
        self.instrument_type=instrument_type
        self.contract_status=contract_status
        self.buy_or_sell=buy_or_sell
        self.counterpart=counterpart
        self.broker = None
        self.contract_owner = None
        self.market=market
        self.trader=trader
        self.marketplace_product=marketplace_product
        self.commodity_delivery_from = None
        self.commodity_delivery_until = None
        self.product_code=None
        self.otc_multi_delivery_periods=[]
        self.certificates=[]
        self.capacity_parameters = []  # Part of contract
        self.contract_tags=[]
        self.area="SYS"
        self.commodity_profile = {}
        self.contract_profile=None

        self.spread = False
        self.otc = False
        self.delivery_type=delivery_type
        self.contract_type=contract_type
        self.contract_sub_type=contract_type  #Default
        self.contract_status_comment=""  # Default
    def update_users_company(self, apiconn):
        prof=UsersApi.get_user_profile(apiconn)
        if prof is None:
            return False
        comp=CustomersApi.get_company_from_registry_number(apiconn,prof['company_nbr'])
        if comp is None:
            return False
        self.contract_owner = comp['pk']  # Being set on contract from current user.
        return True

    def add_contract_tag(self, tag):
        self.contract_tags.append(tag)


    def add_otc_delivery_period(self, delivery_from, delivery_until):
        if isinstance(delivery_from, str):
            self.otc_multi_delivery_periods.append({'period_from': delivery_from,
                                    'period_until': delivery_until,
                                    'price':gen_json_money(self.contract_price),
                                    'quantity': self.quantity})
        else:
            self.otc_multi_delivery_periods.append({'period_from':convert_loc_datetime_to_utcstr(delivery_from),
                                    'period_until':convert_loc_datetime_to_utcstr(delivery_until),
                                    'price':gen_json_money(self.contract_price),
                                    'quantity': self.quantity})

    @staticmethod
    def from_simple_dict(d):
        c=Contract()
        c.pk=d['pk']
        c.instrument_type=d['commodity']['instrument_type']
        c.commodity_type = d['commodity']['commodity_type']
        c.profile_type = ProfileTypeEnum.BASELOAD if 'profile_type' not in d['commodity'] else d['commodity']['profile_type']#
        c.profile_category = ProfileTypeEnum.BASELOAD if d['commodity'][
                                                             'profile_category'] == "BASELOAD" else ProfileTypeEnum.PROFILE.name

        c.delivery_type = d['commodity']['delivery_type']
        c.asset_link = None if 'asset_link' not in d['commodity'] else d['commodity']['asset_link']
        c.commodity_delivery_from = check_fix_date2str(d['commodity']['delivery_from'])
        c.commodity_delivery_until = check_fix_date2str(d['commodity']['delivery_until'])
        c.market = d['commodity']['market']
        c.area = d['commodity']['area']
        c.commodity_profile = d['commodity']['commodity_profile']
        c.spread = d['commodity']['spread']
        c.otc = d['commodity']['otc']
        c.product_code = d['commodity']['product_code']
        c.contract_owner = None if 'contract_owner' not in d else d['contract_owner']
        c.external_contract_id = d['external_contract_id']
        c.trading_book = d['trading_book']
        c.trade_date = check_fix_date2str(d['trade_date'])
        c.trade_datetime = check_fix_date2str(d['trade_time'])
        c.last_update_time = check_fix_date2str(d['last_update_time'])

        c.contract_price = gen_money_from_json(d['contract_price'])
        c.quantity = d['quantity']
        c.quantity_type = QuantityTypeEnum.EFFECT.value if not 'quantity_type' in d else d['quantity_type']
        c.quantity_unit = QuantityUnitEnum.MW.value if not 'quantity_unit' in d else d['quantity_unit']
        c.contract_type=ContractTypeEnum.NASDAQ.value if not 'contract_type' in d else d['contract_type']
        c.trading_fee = gen_money_from_json(d['trading_fee'])
        c.clearing_fee = gen_money_from_json(d['clearing_fee'])
        c.contract_status = d['contract_status']
        c.buy_or_sell = d['buy_or_sell']
        c.counterpart = d['counterpart']
        c.asset_link = None if 'asset_link' not in d else d['asset_link']
        c.trader = d['trader']
        c.marketplace_product = d['marketplace_product']
        for t in d['contract_tags']:
            c.contract_tags.append(ContractTag.from_dict(t))

        c.contract_sub_type=c.contract_type if not 'contract_sub_type' in d else d['contract_sub_type']
        c.contract_status_comment=""  if not 'contract_status_comment' in d else d['contract_status_comment']
        c.broker = d['broker'] if 'broker' in d else None
        return c

    def get_simple_dict(self):
        dict = {}
        dict['pk'] = self.pk
        prod = {}
        if self.asset_link  is not None: prod['asset_link'] = self.asset_link
        if self.instrument_type is not None: prod['instrument_type'] = self.instrument_type.value
        if self.commodity_type is not None: prod['commodity_type'] = self.commodity_type.value
        if self.profile_type is not None: prod['profile_type'] = self.profile_type.value
        if self.profile_category is not None: prod['profile_category'] = str(self.profile_category)

        if self.delivery_type is not None: prod['delivery_type'] = self.delivery_type.value
        if self.commodity_delivery_from is not None: prod['delivery_from'] = self.commodity_delivery_from#check_fix_date2str(
          #  )
        if self.commodity_delivery_until is not None: prod['delivery_until'] = check_fix_date2str(
            self.commodity_delivery_until)
        if self.market is not None: prod['market'] = self.market.value
        prod['area'] = self.area
        prod['commodity_profile'] = self.commodity_profile
        prod['spread'] = self.spread
        prod['otc'] = self.otc
        if self.product_code is not None:
            prod['product_code'] = self.product_code
        else:
            prod['otc'] = True
        dict['commodity'] = prod
        dict['trade_time'] = self.trade_datetime
        #dict['contract_profile']= {} if  self.contract_profile is None else self.contract_profile
        if self.external_contract_id is not None: dict['external_contract_id'] = self.external_contract_id
        if self.trading_book is not None: dict['trading_book'] = self.trading_book
        if self.trade_date is not None: dict['trade_date'] = self.trade_date
        dict['last_update_time'] = self.trade_datetime  # convert_datime_to_utcstr(datetime.now()),
        if self.trade_datetime is not None: dict['trade_time'] = self.trade_datetime
        if self.contract_price is not None: dict['contract_price'] = gen_json_money(self.contract_price)
        if self.quantity is not None: dict['quantity'] = self.quantity
        if self.quantity_type is not None: dict['quantity_type'] = self.quantity_type.value
        if self.quantity_unit is not None: dict['quantity_unit'] = self.quantity_unit.value
        if self.trading_fee is not None: dict['trading_fee'] = gen_json_money(self.trading_fee)
        if self.clearing_fee is not None: dict['clearing_fee'] = gen_json_money(self.clearing_fee)
        if self.contract_type is not None: dict['contract_type'] = self.contract_type.value
        if self.contract_status is not None: dict['contract_status'] = self.contract_status.value

        if self.buy_or_sell is not None: dict['buy_or_sell'] = self.buy_or_sell
        if self.counterpart is not None: dict['counterpart'] = self.counterpart
        if self.broker is not None: dict['broker'] = self.broker
        if self.contract_owner is not None: dict['contract_owner'] = self.contract_owner
        if self.trader is not None: dict['trader'] = self.trader
        if self.marketplace_product is not None: dict[
            'marketplace_product'] = 0

        taglist = []
        for c in self.contract_tags:
            d = c.get_dict()
            taglist.append(d)
        dict['contract_tags'] = taglist
        if len(self.otc_multi_delivery_periods) > 0:
            dict["periods"] = self.otc_multi_delivery_periods
        if len(self.certificates) > 0:
            print("Dicstionaries ", self.certificates)
            dict["certificates"] = self.certificates

        if len(self.capacity_parameters)>0:
            dict["capacity_parameters"] = self.capacity_parameters

        if self.contract_profile is not None:
            dict["contract_profile"] = self.contract_profile.json

        if self.contract_sub_type is not None: dict["contract_sub_type"]=self.contract_sub_type
        if self.contract_status_comment is not None: dict["contract_status_comment"] = self.contract_status_comment
        if self.asset_link is not None: dict['asset_link']=self.asset_link
        return dict


    def get_dict(self, api_conn):
        dict = {}
        dict['pk'] = self.pk
        prod = {}
        if self.instrument_type is not None: prod['instrument_type'] = MarketsApi.get_instrument_type_url(api_conn,self.instrument_type)
        if self.commodity_type is not None: prod['commodity_type'] = MarketsApi.get_commodity_type_url(api_conn, self.commodity_type)
        if self.profile_type is not None: prod['profile_type'] = MarketsApi.get_profile_type_url(api_conn,
                                                                                                       self.profile_type)
        if self.profile_category is not None:
            if type(self.profile_category)==str:
                prod['profile_category'] =self.profile_category
            else:
                prod['profile_category'] = str(self.profile_category.name)
        if self.asset_link is not None: prod['asset_link'] = AssetsApi.get_asset_url(api_conn, self.asset_link)

        if self.delivery_type is not None: prod['delivery_type'] = MarketsApi.get_delivery_type_url(api_conn,
                                                                                                       self.delivery_type)
        if self.commodity_delivery_from is not None:prod['delivery_from'] = check_fix_date2str(self.commodity_delivery_from)
        if self.commodity_delivery_until is not None: prod['delivery_until'] = check_fix_date2str(self.commodity_delivery_until)
        if self.market is not None: prod['market'] = MarketsApi.get_market_url(api_conn, self.market)
        prod['area']=self.area
        #dict['contract_profile'] ={} if  self.contract_profile is None else self.contract_profile
        prod['commodity_profile'] = {} if self.commodity_profile is None else self.commodity_profile
        prod['spread'] = self.spread
        prod['otc'] = self.otc
        if self.product_code is not None:
            prod['product_code'] = self.product_code
        else:
            prod['otc'] = True
        dict['commodity']=prod
        if self.external_contract_id is not None: dict['external_contract_id'] = self.external_contract_id
        if self.trading_book is not None: dict['trading_book'] = TradingBooksApi.get_tradingbook_url(api_conn,self.trading_book)
        s_trade_date=str(self.trade_date)#check_fix_date2str(self.trade_date)
        if s_trade_date is not None:
            dict['trade_date'] = s_trade_date[:10]
        #dict['last_update_time']=self.trade_datetime#convert_datime_to_utcstr(datetime.now()),
        if self.trade_datetime is not None: dict['trade_time'] = check_fix_date2str(self.trade_datetime)
        if self.contract_price is not None: dict['contract_price'] = gen_json_money(self.contract_price)
        if self.quantity is not None: dict['quantity'] = self.quantity
        if self.quantity_unit is not None: dict['quantity_unit'] = ContractsApi.get_quantity_unit_url(api_conn,
                                                                                                            self.quantity_unit)
        if self.quantity_type is not None: dict['quantity_type'] = ContractsApi.get_quantity_type_url(api_conn,
                                                                                                            self.quantity_type)
        if self.trading_fee is not None: dict['trading_fee'] = gen_json_money(self.trading_fee)
        if self.clearing_fee is not None: dict['clearing_fee'] = gen_json_money(self.clearing_fee)
        if self.contract_type is not None: dict['contract_type'] = ContractsApi.get_contract_type_url(api_conn, self.contract_type)
        if self.contract_status is not None: dict['contract_status'] = ContractsApi.get_contract_status_url(api_conn,
                                                                                                            self.contract_status)

        if self.buy_or_sell is not None: dict['buy_or_sell'] = self.buy_or_sell
        if self.contract_owner is not None: dict['contract_owner'] = CustomersApi.get_company_url(api_conn, self.contract_owner)
        if self.counterpart is not None: dict['counterpart'] = CustomersApi.get_company_url(api_conn, self.counterpart)
        if self.broker is not None: dict['broker'] = CustomersApi.get_company_url(api_conn, self.broker)
        if self.trader is not None: dict['trader'] = UsersApi.get_user_url(api_conn, self.trader)
        if self.marketplace_product==0:
            self.marketplace_product=ProductHelper().resolve_ticker(api_conn, self.product_code)
        if self.marketplace_product is not None: dict['marketplace_product'] = api_conn.get_base_url() + "/api/markets/marketproducts/" + str(
                self.marketplace_product) + "/"

        taglist=[]
        for c in self.contract_tags:
            taglist.append(c.get_dict())

        dict['contract_tags']=taglist
        if len(self.otc_multi_delivery_periods) > 0:
            dict["periods"] = self.otc_multi_delivery_periods
        cert_dicts=[]
        for c in self.certificates:
            cert_dicts.append(c.get_dict(api_conn))
        dict["certificates"] = cert_dicts

        capacity_parameters=[]
        for cap in self.capacity_parameters:
            capacity_parameters.append(cap.get_dict(api_conn))
        dict["capacity_parameters"] = capacity_parameters
        if self.contract_profile is not None:
            dict["contract_profile"] = self.contract_profile.json

        if self.contract_sub_type is not None: dict["contract_sub_type"] = self.contract_sub_type
        if self.contract_status_comment is not None: dict["contract_status_comment"] = self.contract_status_comment


        return dict
