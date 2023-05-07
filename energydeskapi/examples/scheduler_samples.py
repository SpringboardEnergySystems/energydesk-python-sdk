
import logging
from energydeskapi.sdk.common_utils import init_api
from energydeskapi.scheduler.scheduler_api import SchedulerApi
import pandas as pd
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])






def schedules(api_conn):
    defs=SchedulerApi.get_job_definitions(api_conn)
    df = pd.DataFrame(data=defs)
    print(df)
    jobs = SchedulerApi.get_scheduled_jobs(api_conn)
    df = pd.DataFrame(data=jobs)
    print(df)


if __name__ == '__main__':

    api_conn=init_api()
    schedules(api_conn)
