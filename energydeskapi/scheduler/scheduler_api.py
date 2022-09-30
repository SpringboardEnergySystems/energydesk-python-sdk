import requests
import json
import logging
import pandas as pd
logger = logging.getLogger(__name__)




class SchedulerApi:
    """ Class for scheduler

    """

    @staticmethod
    def get_scheduled_jobs(api_connection):
        """Fetches scheduled jobs

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobs/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_scheduled_jobs_df(api_connection):
        """Fetches scheduled jobs and shows in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduled-jobs-ext/')
        if json_res is None:
            return None
        print(json_res)
        df = pd.DataFrame(data=json_res)
        return df
