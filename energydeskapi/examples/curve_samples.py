import logging
from energydeskapi.contracts.contracts_api import ContractsApi, Contract
from energydeskapi.gos.gos_api import GosApi, GoContract
from energydeskapi.sdk.common_utils import init_api
from moneyed import EUR
from energydeskapi.curves.curve_api import CurveApi
from energydeskapi.types.location_enum_types import LocationTypeEnum
from datetime import datetime, timedelta
from energydeskapi.sdk.datetime_utils import convert_datime_to_utcstr, convert_datime_to_locstr
from energydeskapi.types.contract_enum_types import ContractStatusEnum, ContractTypeEnum, GosEnergySources
from energydeskapi.types.market_enum_types import CommodityTypeEnum, InstrumentTypeEnum, MarketEnum
from energydeskapi.sdk.money_utils import FormattedMoney
import json
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def get_curves(api_conn):
    fromd="2022-10-01"
    untild = "2024-10-01"
    def process_dframe(df):
        print(df)
        df['date'] = pd.to_datetime(df['date'])
        df.index=df['date']
        df=df[['date', 'price']]
        df2 = df.resample('MS',  on='date').mean()
        print(df2)
        print(df)

    jsonres=CurveApi.get_hourly_price_curve(api_conn, fromd, untild, "NO1", "NOK")

    df = pd.DataFrame(data=eval(jsonres))
    process_dframe(df)
    jsonres=CurveApi.get_hourly_price_curve(api_conn, fromd, untild, "NO5", "NOK")
    if jsonres is not None:
        df = pd.DataFrame(data=eval(jsonres))
        process_dframe(df)

if __name__ == '__main__':
    api_conn=init_api()
    get_curves(api_conn)
