"""
ice_sample.py
=============
Demonstrates querying ICE option underlyings and their options via the
Energydesk REST API using two focused, lightweight calls:

  Step 1 – GET /api/markets/marketproducts/
            ?market_place__name=ICE
            &commodity_definition__instrument_type__code=FUT
            Simple (non-embedded) list of ICE futures.  Fast, small payload.

  Step 2 – For each underlying ticker:
            GET /api/markets/marketproducts/embedded/
            ?market_place__name=ICE
            &commodity_definition__instrument_type__code__in=EUROPT&...=ASIOPT
            &commodity_definition__parameters_for_option__underlying_commodity__product_code=<ticker>
            Returns only the options for that specific underlying – not 1800 records.

REST filter reference (market products):
  market_place__name                                                             = ICE
  commodity_definition__instrument_type__code                                   = FUT | EUROPT | ASIOPT
  commodity_definition__instrument_type__code__in                               = [EUROPT, ASIOPT]
  commodity_definition__parameters_for_option__option_type                      = CALL | PUT
  commodity_definition__parameters_for_option__underlying_commodity__product_code = <ticker>
"""

import logging

from energydeskapi.sdk.common_utils import init_api
from energydeskapi.marketdata.products_api import ProductsApi
from energydeskapi.types.market_enum_types import MarketPlaceEnum, InstrumentTypeEnum, CommodityTypeEnum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("energydesk_client.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Step 1 – Simple list of ICE futures (the option underlyings)
# ──────────────────────────────────────────────────────────────────────────────

def get_ice_futures(api_conn, commodity_type: CommodityTypeEnum = None) -> list[dict]:
    """Return a lightweight list of ICE futures products.

    Uses the plain (non-embedded) marketproducts endpoint so the payload is
    small – we only need the ticker and a few fields to drive the options query.

    Args:
        commodity_type: optional CommodityTypeEnum to narrow results,
                        e.g. CommodityTypeEnum.EUA for emission futures only.
    """
    params = {
        'market_place__name': MarketPlaceEnum.ICE.name,
        'commodity_definition__instrument_type__code': InstrumentTypeEnum.FUT.name,
        'page_size': 500,
    }
    if commodity_type is not None:
        params['commodity_definition__commodity_type__code'] = commodity_type.name

    data = ProductsApi.get_market_products(api_conn, params)
    if not data:
        logger.warning("No ICE futures returned – check connectivity / permissions")
        return []

    futures = []
    for p in data.get('results', []):
        cd = p.get('commodity_definition') or {}
        # commodity_definition is a URL string in the plain serializer;
        # market_ticker is always available directly on the market product.
        futures.append({
            'pk':     p['pk'],
            'ticker': p.get('market_ticker'),
        })

    logger.info(f"Found {len(futures)} ICE futures (total: {data.get('count', '?')})")
    return futures


# ──────────────────────────────────────────────────────────────────────────────
# Step 2 – Options for one underlying (server-side filtered, embedded)
# ──────────────────────────────────────────────────────────────────────────────

def get_options_for_underlying(api_conn, underlying_ticker: str) -> list[dict]:
    """Return option MarketProducts for a single underlying, server-side filtered.

    The appserver filters via:
      commodity_definition__parameters_for_option__underlying_commodity__product_code
    so only options for this specific underlying are returned.

    Use /embedded/ so strike, expiry and option_type come back in one response.

    To narrow further to CALL or PUT add:
      'commodity_definition__parameters_for_option__option_type': 'CALL'
    """
    data = ProductsApi.get_market_products_embedded(api_conn, {
        'market_place__name': MarketPlaceEnum.ICE.name,
        'commodity_definition__instrument_type__code__in': [
            InstrumentTypeEnum.EUROPT.name,
            InstrumentTypeEnum.ASIOPT.name,
        ],
        'commodity_definition__parameters_for_option__underlying_commodity__product_code': underlying_ticker,
        'page_size': 500,
    })
    if not data:
        return []

    results = []
    for product in data.get('results', []):
        cd = product.get('commodity_definition', {})
        for opt in cd.get('parameters_for_option', []):
            results.append({
                'market_product_pk': product['pk'],
                'option_ticker':     cd.get('product_code'),
                'option_type':       opt.get('option_type'),       # CALL / PUT
                'exercise_style':    opt.get('exercise_style'),    # EUROPEAN / ASIAN
                'strike_price':      opt.get('strike_price'),
                'expiration_date':   opt.get('expiration_date'),
            })
            break  # one parameter set per product

    logger.info(
        f"  → {len(results)} options for '{underlying_ticker}' "
        f"(total matched: {data.get('count', '?')})"
    )
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    api_conn = init_api()

    # ── Step 1: ICE emission futures only ────────────────────────────────────
    print("\nStep 1 – fetching ICE emission (EUA) futures…")
    futures = get_ice_futures(api_conn, commodity_type=CommodityTypeEnum.EUA)
    print(f"  {len(futures)} futures found\n")

    if not futures:
        print("  (nothing to query options for)")
    else:
        print("=" * 70)

        # ── Step 2: one targeted options query per underlying ─────────────────
        for fut in futures:
            ticker = fut['ticker']
            print(f"\n  [{ticker}]")

            options = get_options_for_underlying(api_conn, ticker)

            if not options:
                print("    (no options)")
                continue

            # Sort by expiration then strike
            options.sort(key=lambda o: (o['expiration_date'] or '', o['strike_price'] or 0))

            for o in options:
                print(
                    f"    pk={o['market_product_pk']:<6}  "
                    f"{(o['option_ticker'] or '?'):<30s}  "
                    f"{(o['option_type'] or '?'):<4s}  "
                    f"style={o['exercise_style'] or '?':<8s}  "
                    f"strike={o['strike_price']}  "
                    f"exp={o['expiration_date']}"
                )

        print("\n" + "=" * 70)

