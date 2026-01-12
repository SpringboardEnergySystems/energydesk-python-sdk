from unittest import TestCase

from energydeskapi.contracts.contracts_api import Contract
from energydeskapi.sdk.money_utils import CurrencyCode
from energydeskapi.types.contract_enum_types import QuantityUnitEnum
from energydeskapi.types.market_enum_types import ProfileTypeEnum, InstrumentTypeEnum, DeliveryTypeEnum, \
    CommodityTypeEnum


class TestContract(TestCase):
    def test_from_simple_dict(self):
        contract: Contract = Contract.from_simple_dict({'pk': 54925, 'external_contract_id': 'HEV_FASTPRIS_264',
                                   'trading_book': 31,
                                   'trade_date': '2026-01-06', 'trade_time': '2026-01-06T13:07:23Z',
                                   'last_update_time': '2026-01-06T13:10:28.617035Z',
                                   'quantity_type': 2,
                                   'quantity_unit': 2,
                                   'contract_type': 3,
                                   'contract_sub_type': 1,
                                   'contract_status': 2,
                                   'contract_status_comment': None,
                                   'commodity': {'pk': 6539, 'product_code': 'BASELOAD_NO1FEB3YR-26',
                                                 'generic_product_code': None, 'description': 'BASELOAD_NO1FEB3YR-26',
                                                 'area': 'NO1',
                                                 'profile_category': 'BASELOAD',
                                                 'profile_type': 1,
                                                 'structure_type': None,
                                                 'spread': False,
                                                 'asset_link': None,
                                                 'otc': True,
                                                 'delivery_type': 2,
                                                 'delivery_from': '2026-01-31T23:00:00Z',
                                                 'delivery_until': '2029-01-31T23:00:00Z',
                                                 'contract_size': 26304,
                                                 'instrument_type': 2,
                                                 'commodity_type': 1,
                                                 'commodity_profile': {
                                                     'monthly_profile': {'January': 0.08333333333333333,
                                                                         'February': 0.08333333333333333,
                                                                         'March': 0.08333333333333333,
                                                                         'April': 0.08333333333333333,
                                                                         'May': 0.08333333333333333,
                                                                         'June': 0.08333333333333333,
                                                                         'July': 0.08333333333333333,
                                                                         'August': 0.08333333333333333,
                                                                         'September': 0.08333333333333333,
                                                                         'October': 0.08333333333333333,
                                                                         'November': 0.08333333333333333,
                                                                         'December': 0.08333333333333333},
                                                     'weekday_profile': {'Monday': 0.14285714285714285,
                                                                         'Tuesday': 0.14285714285714285,
                                                                         'Wednesday': 0.14285714285714285,
                                                                         'Thursday': 0.14285714285714285,
                                                                         'Friday': 0.14285714285714285,
                                                                         'Saturday': 0.14285714285714285,
                                                                         'Sunday': 0.14285714285714285},
                                                     'daily_profile': {'0': 0.041666666666666664,
                                                                       '1': 0.041666666666666664,
                                                                       '2': 0.041666666666666664,
                                                                       '3': 0.041666666666666664,
                                                                       '4': 0.041666666666666664,
                                                                       '5': 0.041666666666666664,
                                                                       '6': 0.041666666666666664,
                                                                       '7': 0.041666666666666664,
                                                                       '8': 0.041666666666666664,
                                                                       '9': 0.041666666666666664,
                                                                       '10': 0.041666666666666664,
                                                                       '11': 0.041666666666666664,
                                                                       '12': 0.041666666666666664,
                                                                       '13': 0.041666666666666664,
                                                                       '14': 0.041666666666666664,
                                                                       '15': 0.041666666666666664,
                                                                       '16': 0.041666666666666664,
                                                                       '17': 0.041666666666666664,
                                                                       '18': 0.041666666666666664,
                                                                       '19': 0.041666666666666664,
                                                                       '20': 0.041666666666666664,
                                                                       '21': 0.041666666666666664,
                                                                       '22': 0.041666666666666664,
                                                                       '23': 0.041666666666666664}},
                                                 'block_size_category': 8,
                                                 'market': 1,
                                                 'cascaded_date': None},
                                   'contract_owner': 195,
                                   'counterpart': 116,
                                   'broker': None, 'buy_or_sell': 'SELL',
                                   'contract_price': {'amount': 594.7, 'currency': 'NOK'},
                                   'quantity': '50999.9954880000', 'trading_fee': {'amount': 0.0, 'currency': 'EUR'},
                                   'clearing_fee': {'amount': 0.0, 'currency': 'EUR'},
                                   'trader': 70,
                                   'contract_tags': [], 'periods': [], 'contract_profile': {'profile_periods': [
                {'period_from': '2026-02-01T00:00:00+01:00', 'period_until': '2026-03-01T00:00:00+01:00',
                 'period_price': 594.7, 'period_price_currency': 'NOK/MWh', 'period_volume': 1304.109408,
                 'period_effect': 1.940639, 'period_hours': 672.0},
                {'period_from': '2026-03-01T00:00:00+01:00', 'period_until': '2026-04-01T00:00:00+02:00',
                 'period_price': 594.7, 'period_price_currency': 'NOK/MWh', 'period_volume': 1441.894777,
                 'period_effect': 1.940639, 'period_hours': 743.0},
               ]}, 'certificates': [], 'capacity_parameters': [],
                                   'marketplace_product': None, 'linked_contract_id': None,
                                   'cascading_generated': False, 'broker_fee': {'amount': 0.0, 'currency': 'EUR'},
                                   'clearing_commission_fee': {'amount': 0.0, 'currency': 'EUR'}})
        self.assertEqual(contract.pk, 54925)
        self.assertEqual(contract.product_code, 'BASELOAD_NO1FEB3YR-26')
        self.assertEqual(contract.trading_book, 31)
        self.assertEqual(contract.contract_sub_type, 1)
        self.assertEqual(contract.instrument_type, InstrumentTypeEnum.FWD.value)
        self.assertEqual(contract.commodity_delivery_from, '2026-01-31T23:00:00Z')
        self.assertEqual(contract.commodity_delivery_until,  '2029-01-31T23:00:00Z')
        self.assertEqual(contract.external_contract_id, 'HEV_FASTPRIS_264')
        self.assertEqual(contract.commodity_type, CommodityTypeEnum.POWER.value)
        self.assertEqual(contract.area, 'NO1')
        self.assertEqual(contract.delivery_type, DeliveryTypeEnum.PHYSICAL.value)
        self.assertEqual(contract.contract_price.amount.__str__(),  "594.7")
        self.assertEqual(contract.contract_price.currency, CurrencyCode.NOK)
        self.assertEqual(contract.quantity.__str__(), "50999.9954880000")
        self.assertEqual(contract.profile_category, ProfileTypeEnum.BASELOAD)
        self.assertEqual(contract.quantity_unit, QuantityUnitEnum.MW.value)
        self.assertEqual(contract.trader, 70)
