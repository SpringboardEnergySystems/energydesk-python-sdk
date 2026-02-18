from unittest import TestCase

import pandas as pd

from energydeskapi.marketdata.product_utils import is_epad, is_epad_from_trade_values, is_epad_from_series
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


    def test_is_epad_from_series_old_structure_type(self):
        structure_type = pd.Series([StructureTypeEnum.CFD.value, StructureTypeEnum.PLAIN.value, None, StructureTypeEnum.PLAIN.value, None])
        instrument_type = pd.Series([InstrumentTypeEnum.EPAD.name, None, InstrumentTypeEnum.EPAD.name, InstrumentTypeEnum.FUT.name, InstrumentTypeEnum.FUT.name])
        self.assertListEqual(is_epad_from_series(instrument_type, structure_type).tolist(), [True, False, True, False, False])

    def test_is_epad_from_series_new_structure_type(self):
        structure_type = pd.Series([StructureTypeEnum.CFD.value, StructureTypeEnum.PLAIN.value,  StructureTypeEnum.PLAIN.value, StructureTypeEnum.CFD.value, StructureTypeEnum.PLAIN.value])
        instrument_type = pd.Series([InstrumentTypeEnum.FWD.name, InstrumentTypeEnum.FUT.name, InstrumentTypeEnum.FUT.name, InstrumentTypeEnum.FUT.name, InstrumentTypeEnum.FUT.name])
        self.assertListEqual(is_epad_from_series(instrument_type, structure_type).tolist(), [True, False, False, True, False])

