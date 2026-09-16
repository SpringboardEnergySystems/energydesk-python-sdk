"""
Shared, pure derivation compute functions and rule-parameter schemas.

Plan 22 (energydesk-insight, plans/22_vintaged_exposure_and_derived_series.md)
Step C: lifts the option/percentage math out of the appserver's read-time,
today-anchored evaluation path (energydesk/apps/assetdata/timeseries/
expressions/) into pure functions with an explicit ``as_of``. Plan 17
(Derived Forecasts) imports this module rather than reimplementing it —
one set of compute functions, two callers.
"""
