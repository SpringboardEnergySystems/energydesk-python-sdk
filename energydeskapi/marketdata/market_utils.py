from energydeskapi.types.market_enum_types import MarketPlaceEnum, MarketEnum


def get_markets_and_areas(market:MarketEnum):
    if market == MarketEnum.NORDIC_POWER:
        return ["NO1","NO2","NO3", "NO4","NO5","SE1","SE2","SE3","SE4","DK1","DK2", "FI"]
    elif market == MarketEnum.GERMAN_POWER:
        return ["DE"]
    elif market == MarketEnum.GOs_MARKET:
        return ["EUC"]
    else:
        raise ValueError(f"Unsupported market: {market}")

def get_marketplaces_and_areas(market_place:MarketPlaceEnum):
    if market_place == MarketPlaceEnum.EURONEXT:
        return ["NO1","NO2","NO3", "NO4","NO5","SE1","SE2","SE3","SE4","DK1","DK2", "FI"]
    elif market_place == MarketPlaceEnum.EEX:
        return ["DE"]
    elif market_place == MarketPlaceEnum.ICE:
        return ["EUC"]
    else:
        raise ValueError(f"Unsupported market: {market_place}")

def get_countries_and_areas(market:MarketEnum):
    if market == MarketEnum.NORDIC_POWER:
        return {'NORWAY':["NO1","NO2","NO3", "NO4","NO5"],
                "SWEDEN":["SE1","SE2","SE3","SE4"],
                "DENMARK":["DK1","DK2"],
                "FINLAND" :["FI"]}

    elif market == MarketEnum.GERMAN_POWER:
        return {'GERMANY':["DE"]}
    elif market == MarketEnum.GOs_MARKET:
        return {'EUROPE':["EUC"]}
    else:
        raise ValueError(f"Unsupported market: {market}")