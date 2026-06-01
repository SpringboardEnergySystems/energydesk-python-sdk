"""
ice_sample.py
=============
Demonstrates two core ICE option workflows via the Energydesk REST API:

  1. Query option *underlyings* available on ICE
     – Fetch ICE futures products and surface only those that have at least one
       option referencing them as underlying (commodity_definition.underlying_of_option).

  2. For a given underlying ticker, query all *available options* with full
     embedded detail (strike, expiration_date, option_type, exercise_style).

     Two complementary approaches are shown:

     A. /api/markets/commodityoptions/embedded/
        → Returns CommodityOption records.  The embedded underlying_commodity
          carries the full commodity definition (delivery period etc.).
          Best when you need option parameters grouped by the underlying.

     B. /api/markets/marketproducts/embedded/
        → Returns MarketProduct records filtered by marketplace + instrument type.
          The embedded commodity_definition.parameters_for_option carries the
          option parameters (strike, expiry …).
          Best when you also need market product metadata (denomination, pk for
          deal-capture, etc.).

REST filter reference (market products):
  market_place__name                                    = ICE
  commodity_definition__instrument_type__code           = FUT | EUROPT | ASIOPT
  commodity_definition__instrument_type__code__in       = [EUROPT, ASIOPT]  (list)
  commodity_definition__parameters_for_option__option_type = CALL | PUT
"""

import logging
import pprint

from energydeskapi.sdk.common_utils import init_api
from energydeskapi.marketdata.products_api import ProductsApi
from energydeskapi.types.market_enum_types import MarketPlaceEnum, InstrumentTypeEnum

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
# Step 1 – ICE underlyings that have options
# ──────────────────────────────────────────────────────────────────────────────

def get_ice_option_underlyings(api_conn) -> list[dict]:
    """Return ICE futures products that have at least one option on them.

    Queries /api/markets/marketproducts/embedded/ filtered to ICE futures.
    The embedded commodity_definition includes an ``underlying_of_option`` list
    which is non-empty whenever an option product references that future as its
    underlying.

    Returns a list of dicts with keys:
        market_product_pk, ticker, description, delivery_from, delivery_until,
        option_count
    """
    data = ProductsApi.get_market_products_embedded(api_conn, {
        'market_place__name': MarketPlaceEnum.ICE.name,
        'commodity_definition__instrument_type__code': InstrumentTypeEnum.FUT.name,
        'page_size': 500,
    })
    if not data:
        logger.warning("No ICE futures returned – check connectivity / permissions")
        return []

    underlyings = []
    for product in data.get('results', []):
        cd = product.get('commodity_definition', {})
        options_on_this = cd.get('underlying_of_option', [])
        if options_on_this:
            underlyings.append({
                'market_product_pk': product['pk'],
                'ticker':            cd.get('product_code'),
                'description':       cd.get('description'),
                'delivery_from':     cd.get('delivery_from'),
                'delivery_until':    cd.get('delivery_until'),
                'option_count':      len(options_on_this),
            })

    logger.info(f"Found {len(underlyings)} ICE futures with options out of "
                f"{data.get('count', '?')} total ICE futures")
    return underlyings


# ──────────────────────────────────────────────────────────────────────────────
# Step 2A – Options for an underlying via /commodityoptions/embedded/
# ──────────────────────────────────────────────────────────────────────────────

def get_options_for_underlying(api_conn, underlying_ticker: str) -> list[dict]:
    """Return all CommodityOption records for a given underlying ticker.

    Uses GET /api/markets/commodityoptions/embedded/ which returns each option
    with strike_price, expiration_date, option_type (CALL/PUT),
    exercise_style (EUROPEAN/ASIAN) and a fully embedded underlying_commodity.

    Args:
        api_conn:           Initialised ApiConnection.
        underlying_ticker:  product_code of the underlying future,
                            e.g. 'TTF_M_FUT' or 'BRN_M_FUT'.
    """
    data = api_conn.exec_get_url('/api/markets/commodityoptions/embedded/', {
        'page_size': 1000,
    })
    if not data:
        logger.warning("No commodity options returned")
        return []

    options = []
    for opt in data.get('results', []):
        und = opt.get('underlying_commodity', {})
        if und.get('product_code') != underlying_ticker:
            continue

        options.append({
            'option_pk':        opt['pk'],
            # The commodity_definition here is the option product itself
            'option_ticker':    opt.get('commodity_definition', {}).get('product_code'),
            'option_type':      opt.get('option_type'),       # 'CALL' or 'PUT'
            'exercise_style':   opt.get('exercise_style'),    # 'EUROPEAN' or 'ASIAN'
            'strike_price':     opt.get('strike_price'),
            'expiration_date':  opt.get('expiration_date'),
            # Underlying delivery period comes from the embedded underlying_commodity
            'underlying_ticker':   und.get('product_code'),
            'underlying_desc':     und.get('description'),
            'delivery_from':       und.get('delivery_from'),
            'delivery_until':      und.get('delivery_until'),
        })

    logger.info(f"Found {len(options)} options on underlying '{underlying_ticker}'")
    return options


# ──────────────────────────────────────────────────────────────────────────────
# Step 2B – Option *MarketProducts* for an underlying via /marketproducts/embedded/
# ──────────────────────────────────────────────────────────────────────────────

def get_option_market_products_for_underlying(api_conn, underlying_ticker: str) -> list[dict]:
    """Return option MarketProducts on ICE for a given underlying ticker.

    Uses GET /api/markets/marketproducts/embedded/ filtered to option instrument
    types (EUROPT / ASIOPT) on ICE.  The embedded commodity_definition carries
    a parameters_for_option list with strike, expiry, option_type and a minimal
    embedded underlying_commodity.

    Use this approach when you also need the market product pk for deal-capture
    or want to query by option_type (CALL/PUT) server-side.

    Server-side CALL/PUT filter example (add to params dict):
        'commodity_definition__parameters_for_option__option_type': 'CALL'
    """
    data = ProductsApi.get_market_products_embedded(api_conn, {
        'market_place__name': MarketPlaceEnum.ICE.name,
        # Pass a list → serialised as repeated query params by requests lib:
        # ?commodity_definition__instrument_type__code__in=EUROPT
        # &commodity_definition__instrument_type__code__in=ASIOPT
        'commodity_definition__instrument_type__code__in': [
            InstrumentTypeEnum.EUROPT.name,
            InstrumentTypeEnum.ASIOPT.name,
        ],
        'page_size': 1000,
    })
    if not data:
        logger.warning("No ICE option market products returned")
        return []

    results = []
    for product in data.get('results', []):
        cd = product.get('commodity_definition', {})
        for opt_params in cd.get('parameters_for_option', []):
            und = opt_params.get('underlying_commodity', {})
            if und.get('product_code') != underlying_ticker:
                continue
            results.append({
                'market_product_pk':  product['pk'],
                'option_ticker':      cd.get('product_code'),
                'description':        cd.get('description'),
                'instrument_type':    cd.get('instrument_type', {}).get('code'),
                'option_type':        opt_params.get('option_type'),      # CALL / PUT
                'exercise_style':     opt_params.get('exercise_style'),   # EUROPEAN / ASIAN
                'strike_price':       opt_params.get('strike_price'),
                'expiration_date':    opt_params.get('expiration_date'),
                'underlying_ticker':  und.get('product_code'),
            })
            break  # each MarketProduct has one CommodityOption parameter set

    logger.info(
        f"Found {len(results)} option market products on underlying '{underlying_ticker}'"
    )
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    api_conn = init_api()

    # ── 1. List all ICE underlyings that have options ─────────────────────────
    print("\n" + "=" * 70)
    print("STEP 1 – ICE option underlyings")
    print("=" * 70)
    underlyings = get_ice_option_underlyings(api_conn)
    for u in underlyings:
        print(
            f"  pk={u['market_product_pk']:<6d}  "
            f"{u['ticker']:<30s}  "
            f"{(u['description'] or ''):<40s}  "
            f"delivery {u['delivery_from']} → {u['delivery_until']}  "
            f"({u['option_count']} options)"
        )

    if not underlyings:
        print("  (no underlyings found – nothing to query for options)")
    else:
        # Use the first underlying as a demo target
        sample_ticker = underlyings[0]['ticker']

        # ── 2A. Options via commodityoptions/embedded ─────────────────────────
        print(f"\n{'=' * 70}")
        print(f"STEP 2A – Options on '{sample_ticker}'  (via commodityoptions/embedded)")
        print("=" * 70)
        options = get_options_for_underlying(api_conn, sample_ticker)
        for o in options:
            print(
                f"  pk={o['option_pk']:<6d}  "
                f"{(o['option_ticker'] or ''):<30s}  "
                f"{o['option_type']:<4s}  "
                f"style={o['exercise_style']:<8s}  "
                f"strike={o['strike_price']}  "
                f"exp={o['expiration_date']}"
            )

        # ── 2B. Option market products via marketproducts/embedded ─────────────
        print(f"\n{'=' * 70}")
        print(f"STEP 2B – Option market products for '{sample_ticker}'  (via marketproducts/embedded)")
        print("=" * 70)
        mps = get_option_market_products_for_underlying(api_conn, sample_ticker)
        for mp in mps:
            print(
                f"  pk={mp['market_product_pk']:<6d}  "
                f"{(mp['option_ticker'] or ''):<30s}  "
                f"{mp['option_type']:<4s}  "
                f"style={mp['exercise_style']:<8s}  "
                f"strike={mp['strike_price']}  "
                f"exp={mp['expiration_date']}"
            )

