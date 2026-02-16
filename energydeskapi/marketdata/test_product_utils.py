from unittest import TestCase

from energydeskapi.marketdata.product_utils import is_epad, is_epad_from_trade_values
from energydeskapi.types.market_enum_types import InstrumentTypeEnum, StructureTypeEnum


class TestProductUtils(TestCase):
    def test_is_epad(self):
        self.assertTrue(is_epad(InstrumentTypeEnum.FUT, StructureTypeEnum.CFD))
        self.assertTrue(is_epad(InstrumentTypeEnum.EPAD, StructureTypeEnum.CFD))
        self.assertTrue(is_epad(InstrumentTypeEnum.EPAD, None))
        self.assertFalse(is_epad(InstrumentTypeEnum.FWD, None))
        self.assertFalse(is_epad(InstrumentTypeEnum.FUT, None))

    def test_is_epad_from_trade_values(self):
        self.assertTrue(is_epad_from_trade_values(InstrumentTypeEnum.FUT.name, StructureTypeEnum.CFD.value))
        self.assertTrue(is_epad_from_trade_values(InstrumentTypeEnum.EPAD.name, StructureTypeEnum.CFD.value))
        self.assertTrue(is_epad_from_trade_values(InstrumentTypeEnum.EPAD.name, None))
        self.assertFalse(is_epad_from_trade_values(InstrumentTypeEnum.FWD.name, None))
        self.assertFalse(is_epad_from_trade_values(InstrumentTypeEnum.FUT.name, None))
