
import pandas as pd
import numpy as np

def recalculate_sys(df: pd.DataFrame, combine_area_types: bool=True) -> pd.DataFrame:
    """
    Re-calculate SYS per area by extracting EPAD-volum in a SYS-leg with price 0.

    For every period t:
      Q_sys_new(t) = Q_sys_old(t) - sum_{EPAD, area!=SYS} q_epad(t)
      K_sys_new(t) = (Q_sys_old(t)*K_sys_old(t)) / Q_sys_new(t)   (0 if Q_sys_new == 0)

    - Output: one row per (period, area, type) with volum-weighted avgcost.
    - If a period has EPAD but no SYS: Q_sys_new = -sum_EPAD, K_sys_new = 0.
    - If a period only has AREA (no EPAD, no SYS): Q_sys_new = 0, K_sys_new = 0.

    If you sell a 50 MWh NO1 EPAD at 10 EUR/MWh, do the following:
    Sell 50 MWh NO1 at 10 EUR/MWh
    Buy 50 MWh SYS at 0 EUR/MWh
    """

    if df is None or df.empty:
        out = df.copy()
        if "type" not in out.columns:
            out["type"] = None
        return out

    x = df.copy()
    keep = [c for c in ["period", "area", "type", "netvol", "avgcost"] if c in x.columns]
    x = x[keep].copy()
    x["period"] = pd.to_datetime(x["period"])

    # If 'type' is completely missing, best-effort (SYS -> AREA, else EPAD)
    if "type" not in x.columns or x["type"].isna().all():
        x["type"] = np.where(x["area"] == "SYS", "AREA", "EPAD")

    # Collapse to one row per (period, area, type) with volume-weighted avgcost
    x["_cost"] = x["netvol"] * x["avgcost"]
    collapsed = (
        x.groupby(["period", "area", "type"], as_index=False)
         .agg(netvol=("netvol", "sum"), cost=(" _cost".strip(), "sum"))
    )
    nz = collapsed["netvol"] != 0
    collapsed["avgcost"] = 0.0
    collapsed.loc[nz, "avgcost"] = collapsed.loc[nz, "cost"] / collapsed.loc[nz, "netvol"]
    collapsed = collapsed[["period", "area", "type", "netvol", "avgcost"]]

    # EPAD-volum per area (all areas except SYS) per periode
    epad_sum = (
        collapsed[(collapsed["type"] == "EPAD") & (collapsed["area"] != "SYS")]
        .groupby("period")
        .agg(epad_sum=("netvol", "sum"))
    )

    # SYS per period: only cost/volume from original SYS contracts
    sys_old_rows = collapsed[(collapsed["area"] == "SYS") & (collapsed["type"] == "AREA")].copy()
    if sys_old_rows.empty:
        sys_old = pd.DataFrame(index=pd.DatetimeIndex([], name="period"),
                               data={"sys_netvol": [], "sys_cost": []})
    else:
        sys_old_rows["_cost"] = sys_old_rows["netvol"] * sys_old_rows["avgcost"]
        sys_old = (sys_old_rows.groupby("period")
                   .agg(sys_netvol=("netvol", "sum"),
                        sys_cost=("_cost", "sum")))

    # Adjust indexes, ensure all periods are included
    periods = pd.DatetimeIndex(pd.to_datetime(collapsed["period"]).dt.normalize().unique())
    sys_old.index  = pd.DatetimeIndex(pd.to_datetime(sys_old.index).normalize())
    epad_sum.index = pd.DatetimeIndex(pd.to_datetime(epad_sum.index).normalize())
    periods = periods.union(sys_old.index).union(epad_sum.index)

    # Re-calculate SYS: EPAD contributions always have price 0 
    sys_old = sys_old.reindex(periods, fill_value=0.0)
    epad_sum = epad_sum.reindex(periods, fill_value=0.0)

    sys_new = pd.DataFrame(index=periods)
    # Volume: extract EPAD volume (SYS contribution from EPAD = -q_epad)
    sys_new["netvol"] = sys_old["sys_netvol"] - epad_sum["epad_sum"]

    # Price: only cost from old SYS contracts; EPAD contributions have price 0
    with np.errstate(divide="ignore", invalid="ignore"):
        # handle division by zero
        sys_new["avgcost"] = np.where(
            sys_new["netvol"] != 0,
            sys_old["sys_cost"] / sys_new["netvol"],
            0.0,
        )

    sys_new = (sys_new.reset_index()
                     .rename(columns={"index": "period"})
                     .assign(area="SYS", type="AREA"))

    # Combine: keep all non-SYS (EPAD/AREA) separate + new SYS
    non_sys = collapsed[collapsed["area"] != "SYS"][["period", "area", "type", "netvol", "avgcost"]]
    if combine_area_types:
        # EPAD adds to area; AREA adds to area => merge both for each (period, area != SYS)
        non_sys = collapsed[collapsed["area"] != "SYS"].copy()
        non_sys["_cost"] = non_sys["netvol"] * non_sys["avgcost"]
        area_tot = (
            non_sys.groupby(["period", "area"], as_index=False)
                   .agg(netvol=("netvol", "sum"), cost=("_cost", "sum"))
        )
        area_tot["avgcost"] = 0.0
        nz = area_tot["netvol"] != 0
        area_tot.loc[nz, "avgcost"] = area_tot.loc[nz, "cost"] / area_tot.loc[nz, "netvol"]
        area_tot = area_tot[["period", "area", "netvol", "avgcost"]]
        area_tot["type"] = "AREA"
        out = pd.concat(
            [area_tot[["period", "area", "type", "netvol", "avgcost"]],
             sys_new[["period", "area", "type", "netvol", "avgcost"]]],
            ignore_index=True
        )
    else:
        # Original behavior: keep AREA and EPAD separate for non-SYS; only SYS is recomputed
        non_sys = collapsed[collapsed["area"] != "SYS"][["period", "area", "type", "netvol", "avgcost"]]
        out = pd.concat(
            [non_sys, sys_new[["period", "area", "type", "netvol", "avgcost"]]],
            ignore_index=True
        )

    return out.sort_values(["period", "area", "type"]).reset_index(drop=True)[
        ["period", "area", "type", "netvol", "avgcost"]
    ]