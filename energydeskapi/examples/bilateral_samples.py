import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from moneyed import EUR
from energydeskapi.bilateral.bilateral_api import BilateralApi
from energydeskapi.types.location_enum_types import LocationTypeEnum
from datetime import datetime, timedelta
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr, convert_datime_to_locstr
from energydeskapi.types.contract_enum_types import ContractStatusEnum, ContractTypeEnum, GosEnergySources
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
from energydeskapi.sdk.money_utils import FormattedMoney
from energydeskapi.types.fwdcurve_enum_types import FwdCurveInternalEnum
import json
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def calculate_price(api_conn):
    fromd="2023-10-01"
    untild = "2024-10-01"

    success, res, status_code, error_msg =BilateralApi.calculate_contract_price(api_conn,fromd, untild,10, "NO1", "NOK",
                                            FwdCurveInternalEnum.CUBIC_SPLINE.value)


    df_curve = pd.DataFrame(data=eval(res['forward_curve']))
    df_pricing = pd.DataFrame(data=eval(res['pricing_details']))
    contract_price=res['contract_price']

    print(df_pricing)
    print("Contract price", contract_price)


if __name__ == '__main__':
    api_conn=init_api()
    calculate_price(api_conn)
