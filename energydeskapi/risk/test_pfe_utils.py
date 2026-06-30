"""Tests for the shared PFE period-view helpers in pfe_utils.

assign_position_type / filter_pfe_areas were extracted here so var-service and
the portal classify the period view identically. The key regression guarded:
EPAD must be detected from structure_type (CFD==2), NOT from the area name --
the backend switched from 'SYSNO1'-style areas to bare 'NO1'/'SYS', which broke
any area-name heuristic and made recalculate_sys extract nothing into SYS.
"""
from unittest import TestCase

import pandas as pd

from energydeskapi.risk.pfe_utils import (
    PFE_ALLOWED_AREAS,
    assign_position_type,
    filter_pfe_areas,
    recalculate_sys,
)
from energydeskapi.types.market_enum_types import StructureTypeEnum

CFD = StructureTypeEnum.CFD.value      # 2 -> EPAD (area-vs-SYS spread)
PLAIN = StructureTypeEnum.PLAIN.value  # 1 -> system / plain area contract


def _new_style_rows():
    """Post-change naming: bare areas ('NO5'/'SYS'), type lives in structure_type."""
    period = pd.Timestamp("2027-01-01")
    return pd.DataFrame([
        {"period": period, "area": "NO5", "structure_type": CFD,
         "instrument": "FWD", "netvol": 60.0, "avgcost": 8.0},
        {"period": period, "area": "SYS", "structure_type": PLAIN,
         "instrument": "FWD", "netvol": -100.0, "avgcost": 40.0},
    ])


class TestAssignPositionType(TestCase):
    def test_epad_from_structure_type_not_area_name(self):
        out = assign_position_type(_new_style_rows())
        types = dict(zip(out["area"], out["type"]))
        self.assertEqual(types["NO5"], "EPAD")
        self.assertEqual(types["SYS"], "AREA")

    def test_plain_area_contract_is_not_epad(self):
        rows = _new_style_rows()
        rows.loc[len(rows)] = {"period": pd.Timestamp("2027-01-01"), "area": "NO1",
                               "structure_type": PLAIN, "instrument": "FUT",
                               "netvol": 10.0, "avgcost": 30.0}
        out = assign_position_type(rows)
        self.assertEqual(out[out["area"] == "NO1"]["type"].tolist(), ["AREA"])

    def test_input_frame_not_mutated(self):
        rows = _new_style_rows()
        assign_position_type(rows)
        self.assertNotIn("type", rows.columns)

    def test_no_structure_type_falls_back_to_instrument(self):
        rows = _new_style_rows().drop(columns=["structure_type"])
        rows["instrument"] = ["EPAD", "FWD"]
        out = assign_position_type(rows)
        self.assertEqual(dict(zip(out["area"], out["type"])),
                         {"NO5": "EPAD", "SYS": "AREA"})


class TestFilterPfeAreas(TestCase):
    def test_drops_illegal_areas(self):
        rows = _new_style_rows()
        rows.loc[len(rows)] = {"period": pd.Timestamp("2027-01-01"), "area": "DE",
                               "structure_type": PLAIN, "instrument": "FUT",
                               "netvol": 1.0, "avgcost": 1.0}
        out = filter_pfe_areas(rows)
        self.assertEqual(set(out["area"]), {"NO5", "SYS"})
        self.assertTrue(set(out["area"]).issubset(set(PFE_ALLOWED_AREAS)))


class TestRecalculateSysWithEpad(TestCase):
    def test_epad_volume_extracted_into_sys(self):
        out = recalculate_sys(assign_position_type(_new_style_rows()))
        sys = out[out["area"] == "SYS"].iloc[0]
        # sys_new = -100 - (+60) = -160 ; avgcost = (-100*40)/-160 = 25
        self.assertAlmostEqual(sys["netvol"], -160.0, places=6)
        self.assertAlmostEqual(sys["avgcost"], 25.0, places=6)

    def test_exact_cancellation_preserves_cost_via_nudge(self):
        rows = _new_style_rows()
        rows.loc[rows["area"] == "SYS", "netvol"] = 60.0   # cancels the EPAD vol
        rows.loc[rows["area"] == "SYS", "avgcost"] = 40.0
        out = recalculate_sys(assign_position_type(rows))
        sys = out[out["area"] == "SYS"].iloc[0]
        self.assertNotEqual(sys["netvol"], 0.0)
        self.assertGreater(abs(sys["avgcost"]), 1e6)
