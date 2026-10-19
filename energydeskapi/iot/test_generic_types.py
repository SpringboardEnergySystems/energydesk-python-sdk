import pytest

from energydeskapi.iot.generic_types import GenericMetric, derive_generic_points

KEY = GenericMetric.ACTIVE_POWER_KW


@pytest.mark.parametrize("resource_type, points, expected", [
    ("solar", {"solar_kw": 3.0}, -3.0),
    ("solar", {"pvpowerout": 2000.0}, -2.0),
    ("solar", {"grid_active_power": -4.2}, -4.2),
    ("solar", {"solar_kw": 3.0, "pvpowerout": 9000.0}, -3.0),      # priority order
    ("battery", {"grid_active_power": 1.5, "battery_power_kw": 2.0}, 1.5),
    ("battery", {"battery_power_kw": 2.0}, -2.0),                   # discharge = generation
    ("main_meter", {"active_power": 272.0}, 0.272),
    ("heat_pump", {"grid_active_power": 2.5}, 2.5),
    ("ev_charger", {"grid_active_power": 7.4}, 7.4),
])
def test_derives_active_power_kw(resource_type, points, expected):
    assert derive_generic_points(resource_type, points) == {KEY: pytest.approx(expected)}


@pytest.mark.parametrize("resource_type, points", [
    ("main_meter", {KEY: 0.3, "active_power": 272.0}),   # device's own value wins
    ("solar", {"unrelated": 1.0}),
    ("other", {"grid_active_power": 1.0}),
    (None, {"grid_active_power": 1.0}),
])
def test_derives_nothing(resource_type, points):
    assert derive_generic_points(resource_type, points) == {}


def test_no_negative_zero():
    assert str(derive_generic_points("solar", {"solar_kw": 0.0})[KEY]) == "0.0"
