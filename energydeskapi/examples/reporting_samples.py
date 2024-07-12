import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.reporting.report_config_api import ReportConfigApi, ReportConfig
from energydeskapi.types.company_enum_types import UserRoleEnum
from energydeskapi.sdk.datetime_utils import prev_weekday
from datetime import datetime
from energydeskapi.sdk.crontab_utils import generate_dataframe
from dateutil.relativedelta import relativedelta
import pytz
import pandas as pd
from energydeskapi.sdk.pandas_utils import make_empty_timeseries_df
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])


def load_report_config(api_conn):
    data=ReportConfigApi.get_report_configs(api_conn)
    print(data)
    df=pd.DataFrame(data['results'])
    print(df)

if __name__ == '__main__':
    api_conn = init_api()

    load_report_config(api_conn)