from energydeskapi.types.market_enum_types import MarketEnum, ProfileTypeEnum


def lookup_profile_description(atype):
    if atype==ProfileTypeEnum.BASELOAD:
        return "Baseload"
    elif atype==ProfileTypeEnum.PROFILE:
        return "Relative Profile"
    elif atype==ProfileTypeEnum.ABSOLUTEPROFILE:
        return "Absolute Profile"
    else:
        return "Unknown Profile"

def lookup_market_description(market_enum):
    if market_enum==MarketEnum.NORDIC_POWER:
        return "Nordic Power"
    elif market_enum==MarketEnum.GERMAN_POWER:
        return "German Power"
    elif market_enum==MarketEnum.CARBON_EMISSIONS:
        return "European Carbon Market"
    elif market_enum==MarketEnum.CURRENCY_MARKET:
        return "Currency Market"
    elif market_enum==MarketEnum.GOs_MARKET:
        return "European GoO Market"
    return "Unknown Market"
