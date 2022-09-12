import sys

import requests
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.scheduler.scheduler_api import SchedulerApi

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])




def schedules(api_conn):
    df=SchedulerApi.get_scheduled_jobs_df(api_conn)
    #df=TreasuryApi.get_treasury_banks(api_conn)
    print(df)
    jobs = SchedulerApi.get_scheduled_jobs(api_conn)
    print(jobs)


if __name__ == '__main__':

    api_conn=init_api()
    schedules(api_conn)
