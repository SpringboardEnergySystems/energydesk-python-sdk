"""
Register ICE (Intercontinental Exchange) and ICE Clear Europe as companies
in the Energydesk platform.

ICE Clear Europe is the central counterparty (CCP) for ICE futures markets,
including natural gas (TTF, NBP) and other commodity futures.

For clearing access, most participants use a General Clearing Member (GCM)
such as SEB. In that case:
  - The 'counterpart' on the contract = your GCM (e.g. SEB)
  - The 'counterpart_type' on the contract = ICE (CounterpartTypeEnum.ICE)

If you are a direct clearing member, set ICE Clear Europe as the counterpart.
"""

import logging

from energydeskapi.sdk.common_utils import init_api
from energydeskapi.customers.customers_api import CustomersApi, Company
from energydeskapi.types.company_enum_types import CompanyTypeEnum, CompanyRoleEnum

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

logger = logging.getLogger(__name__)


def register_ice_clear_europe(api_conn):
    """Register ICE Clear Europe as a Clearing House company."""
    c = Company()
    c.name = "ICE Clear Europe"
    c.alias = "ICE"
    c.lei_code = "W22LROWP2IHZNBB6K528"  # ICE Clear Europe LEI
    c.company_type = CustomersApi.get_company_type_url(
        api_conn, CompanyTypeEnum.SERVICE_COMPANY
    )
    c.company_roles = [
        CustomersApi.get_company_role_url(api_conn, CompanyRoleEnum.CLEARING_HOUSE)
    ]
    c.address = "Milton Gate, 60 Chiswell Street"
    c.postal_code = "EC1Y 4SA"
    c.city = "London"
    c.country = "GB"
    c.location = "51.520718,-0.090614"

    success, json_res, status_code, error_msg = CustomersApi.upsert_company(api_conn, c)
    if success:
        logger.info(f"ICE Clear Europe registered/updated: pk={json_res.get('pk')}")
    else:
        logger.error(f"Failed to register ICE Clear Europe: {error_msg}")
    return json_res


def query_clearing_houses(api_conn):
    """List all companies with CLEARING_HOUSE role."""
    param = {'company_roles': CompanyRoleEnum.CLEARING_HOUSE.value, "page_size": 50}
    json_companies = CustomersApi.get_companies(api_conn, param)
    results = json_companies.get('results', [])
    for c in results:
        print(f"  pk={c['pk']}  {c['name']}  alias={c.get('alias')}")
    return results


if __name__ == '__main__':
    api_conn = init_api()

    print("\n--- Existing clearing houses ---")
    query_clearing_houses(api_conn)

    print("\n--- Registering ICE Clear Europe ---")
    register_ice_clear_europe(api_conn)

    print("\n--- Clearing houses after registration ---")
    query_clearing_houses(api_conn)

