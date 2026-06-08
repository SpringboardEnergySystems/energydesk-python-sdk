"""
ice_sample.py
=============
Demonstrates querying ICE option products and fetching the latest closing price
for specific options — using plain HTTP calls to the Energydesk REST API.

No SDK wrappers required.  Only the standard library + ``requests`` is needed.

Endpoints used
──────────────
  GET /api/markets/marketproducts/
      List ICE futures (underlyings).
      Key filters:
        market_place__name                               = ICE
        commodity_definition__instrument_type__code     = FUT | EUROPT | ASIOPT
        commodity_definition__commodity_type__code      = EUA  (optional, narrow to emissions)

  GET /api/markets/marketproducts/embedded/
      Same as above but commodity_definition is fully inlined, including the
      nested parameters_for_option list (strike, expiry, option_type, …).

  GET /api/markets/productprices/
      Product settlement/closing prices.
      Key filters:
        product__market_ticker__in  = <ticker>   (repeatable)
        price_date__gte             = YYYY-MM-DD (default: today)
        page_size                   = N

  POST /api/portfoliomanager/contracts/
      Register a buy/sell contract.  For ICE emission options use:
        contract_type  pk=14  (ICE_EMISSION_OPTIONS)
        trading_book   pk=82  (EMISSION_OPTIONS)
        quantity_type  pk=7   (LOTS)
        quantity_unit  pk=5   (LOTS)
        counterpart    pk=800 (ICE Futures Europe)

Authentication
──────────────
  Set the TOKEN variable below, or export ENERGYDESK_TOKEN before running.
  The server expects a DRF token header:  Authorization: Token <token>

Usage
─────
  python ice_sample.py
"""

import argparse
import logging
import os
import sys
import uuid
from datetime import datetime, timezone

import requests

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_URL = os.environ.get("ENERGYDESK_URL", "http://localhost:8001")
TOKEN    = os.environ.get("ENERGYDESK_TOKEN", "your-token-here")

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type":  "application/json",
}

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("energydesk_client.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get(path: str, params: dict) -> dict:
    """GET a paginated endpoint and return the raw JSON response dict."""
    url = f"{BASE_URL}/api/{path.lstrip('/')}"
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    if not resp.ok:
        logger.error(f"GET {url} returned {resp.status_code}: {resp.text[:200]}")
        resp.raise_for_status()
    return resp.json()


def post(path: str, payload: dict) -> dict:
    """POST to an endpoint and return the response JSON."""
    url = f"{BASE_URL}/api/{path.lstrip('/')}"
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    if not resp.ok:
        logger.error(f"POST {url} returned {resp.status_code}: {resp.text[:400]}")
        resp.raise_for_status()
    return resp.json()


# ── Lookup helpers ────────────────────────────────────────────────────────────

ICE_LEI = "549300UF4R84F48NCH34"

def lookup_company_url_by_lei(lei: str) -> str:
    """Return the hyperlink URL for a company identified by its LEI code."""
    data = get("customers/companies/", {"lei_code": lei, "page_size": 5})
    results = data.get("results", [])
    if not results:
        raise ValueError(f"No company found with LEI '{lei}'")
    return f"{BASE_URL}/api/customers/companies/{results[0]['pk']}/"


def lookup_trading_book_url(name: str) -> str:
    """Return the hyperlink URL for the first trading book whose description matches name (case-insensitive)."""
    data = get("portfoliomanager/tradingbooks/", {"page_size": 200})
    for book in data.get("results", []):
        if book["description"].lower() == name.lower():
            return f"{BASE_URL}/api/portfoliomanager/tradingbooks/{book['pk']}/"
    raise ValueError(f"No trading book found with description '{name}'")


# ── Step 3 – Register a BUY order ────────────────────────────────────────────

def register_buy_order(option_ticker: str, price: float, counterpart_url: str,
                       trading_book_url: str, quantity: float = 1.0) -> dict:
    """Register a BUY contract for an ICE emission PUT option.

    Args:
        option_ticker:    The option's market ticker, e.g. 'FEUA122026P095'.
        price:            Contract price in EUR.
        counterpart_url:  Full hyperlink URL of the counterpart company.
        trading_book_url: Full hyperlink URL of the trading book.
        quantity:         Quantity in lots (default 1).

    Returns:
        The created contract object from the server.
    """
    now = datetime.now(timezone.utc)
    trade_date = now.strftime("%Y-%m-%d")
    trade_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    external_id = f"ICE-OPT-{trade_date}-{uuid.uuid4().hex[:8].upper()}"

    payload = {
        "pk": 0,
        "external_contract_id": external_id,
        "commodity": {
            "product_code": option_ticker,
            "commodity_profile": None,
        },
        "trading_book":            trading_book_url,
        "trade_date":              trade_date,
        "trade_time":              trade_time,
        "contract_type":           f"{BASE_URL}/api/portfoliomanager/contracttypes/14/",
        "contract_status":         f"{BASE_URL}/api/portfoliomanager/contractstatuses/1/",
        "buy_or_sell":             "BUY",
        "contract_price":          {"amount": round(price, 4), "currency": "EUR"},
        "quantity":                quantity,
        "quantity_type":           f"{BASE_URL}/api/portfoliomanager/quantitytypes/7/",
        "quantity_unit":           f"{BASE_URL}/api/portfoliomanager/quantityunits/5/",
        "trading_fee":             {"amount": 0.0, "currency": "EUR"},
        "clearing_fee":            {"amount": 0.0, "currency": "EUR"},
        "clearing_commission_fee": {"amount": 0.0, "currency": "EUR"},
        "broker_fee":              {"amount": 0.0, "currency": "EUR"},
        "counterpart":             counterpart_url,
        "contract_tags":           [],
        "certificates":            [],
        "capacity_parameters":     [],
        "cascading_generated":     False,
    }
    return post("portfoliomanager/contracts/", payload)


# ── Step 1 – ICE emission futures ─────────────────────────────────────────────

def get_ice_futures(commodity_type_code: str = None) -> list[dict]:
    """Return a list of ICE futures (underlyings).

    Args:
        commodity_type_code: optional commodity type code to narrow results,
                             e.g. 'EUA' for emission futures only.
    """
    params = {
        "market_place__name": "ICE",
        "commodity_definition__instrument_type__code": "FUT",
        "page_size": 500,
    }
    if commodity_type_code:
        params["commodity_definition__commodity_type__code"] = commodity_type_code

    data = get("markets/marketproducts/", params)
    results = data.get("results", [])
    logger.info(f"Found {len(results)} ICE futures (total: {data.get('count', '?')})")
    return results


# ── Step 2 – Options for one underlying ───────────────────────────────────────

def get_options_for_underlying(underlying_ticker: str) -> list[dict]:
    """Return option MarketProducts for a single underlying, fully embedded.

    Uses the /embedded/ action so strike, expiry, and option_type are inlined.
    """
    params = {
        "market_place__name": "ICE",
        "commodity_definition__instrument_type__code__in": ["EUROPT", "ASIOPT"],
        "commodity_definition__parameters_for_option__underlying_commodity__product_code": underlying_ticker,
        "page_size": 500,
    }
    data = get("markets/marketproducts/embedded/", params)
    results_raw = data.get("results", [])

    options = []
    for product in results_raw:
        cd = product.get("commodity_definition") or {}
        for opt in cd.get("parameters_for_option") or []:
            options.append({
                "market_product_pk": product["pk"],
                "option_ticker":     cd.get("product_code"),
                "market_ticker":     product.get("market_ticker"),
                "option_type":       opt.get("option_type"),
                "exercise_style":    opt.get("exercise_style"),
                "strike_price":      opt.get("strike_price"),
                "expiration_date":   opt.get("expiration_date"),
            })
            break  # one parameter set per product

    logger.info(
        f"  → {len(options)} options for '{underlying_ticker}' "
        f"(total matched: {data.get('count', '?')})"
    )
    return options


# ── Step 3 – Latest price for a ticker ────────────────────────────────────────

def get_latest_price(ticker: str) -> dict | None:
    """Fetch the most recent settlement price record for a product ticker.

    The productprices endpoint defaults to today's date when no price_date__gte
    is supplied.  We request page_size=1 with ordering by -price_date.
    """
    params = {
        "product__market_ticker__in": ticker,
        "price_date__gte": "2000-01-01",
        "page_size": 1,
    }
    data = get("markets/productprices/", params)
    results = data.get("results", [])
    return results[0] if results else None


# ── Mode: list ────────────────────────────────────────────────────────────────

def run_list(trading_book_url: str) -> None:
    """Print all contracts booked in the Emission Options trading book."""
    # Extract pk from the URL for the filter parameter
    book_pk = trading_book_url.rstrip("/").split("/")[-1]
    page, total = 1, None
    contracts = []
    while total is None or len(contracts) < total:
        data = get("portfoliomanager/contracts/", {"trading_book": book_pk, "page_size": 100, "page": page})
        total = data.get("count", 0)
        batch = data.get("results", [])
        if not batch:
            break
        contracts.extend(batch)
        page += 1

    print(f"\n{'='*80}")
    print(f"  Emission Options trading book — {len(contracts)} contract(s)")
    print(f"{'='*80}")
    print(f"  {'pk':<8}  {'external_id':<36}  {'B/S':<4}  {'ticker':<30}  {'price':>8}  {'qty':>5}  {'status'}")
    print(f"  {'-'*8}  {'-'*36}  {'-'*4}  {'-'*30}  {'-'*8}  {'-'*5}  {'-'*12}")
    for c in contracts:
        commodity   = c.get("commodity") or {}
        price_obj   = c.get("contract_price") or {}
        status_url  = c.get("contract_status", "")
        status_pk   = status_url.rstrip("/").split("/")[-1] if status_url else "?"
        status_map  = {"1": "REGISTERED", "2": "CONFIRMED", "3": "APPROVED", "4": "CANCELLED", "5": "PROPOSAL", "6": "PENDING"}
        print(
            f"  {c.get('pk', '?'):<8}  "
            f"{c.get('external_contract_id', '?'):<36}  "
            f"{c.get('buy_or_sell', '?'):<4}  "
            f"{commodity.get('product_code', '?'):<30}  "
            f"{float(price_obj.get('amount', 0)):>8.4f}  "
            f"{float(c.get('quantity', 0)):>5.1f}  "
            f"{status_map.get(status_pk, status_pk)}"
        )
    print(f"{'='*80}\n")


# ── Mode: create ──────────────────────────────────────────────────────────────

def run_create(counterpart_url: str, trading_book_url: str) -> None:
    """Scan ICE EUA options and place BUY orders on all strike-95 PUTs."""
    print("\nStep 1 – fetching ICE emission (EUA) futures…")
    futures = get_ice_futures(commodity_type_code="EUA")
    print(f"  {len(futures)} futures found\n")

    if not futures:
        print("  (nothing to query options for)")
        return

    print("=" * 70)

    for fut in futures:
        ticker = fut.get("market_ticker")
        print(f"\n  [{ticker}]")

        options = get_options_for_underlying(ticker)

        if not options:
            print("    (no options)")
            continue

        options.sort(key=lambda o: (o["expiration_date"] or "", float(o["strike_price"] or 0)))

        for o in options:
            print(
                f"    pk={o['market_product_pk']:<6}  "
                f"{(o['option_ticker'] or '?'):<30s}  "
                f"{(o['option_type'] or '?'):<4s}  "
                f"style={o['exercise_style'] or '?':<8s}  "
                f"strike={o['strike_price']}  "
                f"exp={o['expiration_date']}"
            )

            if float(o["strike_price"] or 0) == 96 and o["option_type"] in ("PUT", "P"):
                print(f"    *** Strike-96 PUT found: {o['option_ticker']}")
                price_rec = get_latest_price(o["market_ticker"] or o["option_ticker"])
                if price_rec:
                    close = float(price_rec.get("close") or price_rec.get("last") or 0)
                    print(
                        f"        Latest price: close={close}  last={price_rec.get('last')}  "
                        f"date={price_rec.get('price_date')}"
                    )
                else:
                    print(f"        No price data found for {o['market_ticker'] or o['option_ticker']}")

            if float(o["strike_price"] or 0) == 95 and o["option_type"] in ("PUT", "P"):
                opt_ticker = o["market_ticker"] or o["option_ticker"]
                print(f"    *** Strike-95 PUT found: {opt_ticker} — fetching price for order…")
                price_rec = get_latest_price(opt_ticker)
                if price_rec:
                    close = float(price_rec.get("close") or price_rec.get("last") or 0)
                    order_price = round(close - 0.01, 4)
                    print(f"        Market close={close}  →  order price={order_price} EUR  qty=1 lot")
                    try:
                        result = register_buy_order(opt_ticker, order_price, counterpart_url, trading_book_url, quantity=1.0)
                        print(f"        Order registered: pk={result.get('pk')}  id={result.get('external_contract_id')}")
                    except Exception as e:
                        print(f"        Order FAILED: {e}")
                else:
                    print(f"        No price data found — cannot place order for {opt_ticker}")

    print("\n" + "=" * 70)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ICE EUA option tool — query products, fetch prices, register orders.",
    )
    parser.add_argument(
        "mode",
        choices=["create", "list"],
        help=(
            "create: scan ICE EUA PUT options at strike 95 and register BUY orders; "
            "list:   show all contracts booked in the Emission Options trading book"
        ),
    )
    args = parser.parse_args()

    if TOKEN == "your-token-here":
        print("ERROR: set ENERGYDESK_TOKEN environment variable before running.")
        sys.exit(1)

    # Resolve FK URLs dynamically (needed by both modes)
    print("Resolving trading book…")
    trading_book_url = lookup_trading_book_url("Emission Options")
    print(f"  trading book: {trading_book_url}")

    if args.mode == "list":
        run_list(trading_book_url)

    elif args.mode == "create":
        print("Resolving counterpart (ICE Futures Europe)…")
        counterpart_url = lookup_company_url_by_lei(ICE_LEI)
        print(f"  counterpart:  {counterpart_url}")
        run_create(counterpart_url, trading_book_url)
