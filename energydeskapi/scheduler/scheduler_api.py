import logging
import pandas as pd
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)

@dataclass
class ScheduledJob:
    pk: int
    job_definition: str
    crontab: str
    dynamic_parameter: str
    is_active: bool


class SchedulerApi:
    """ Class for scheduler

    """

    @staticmethod
    def upsert_scheduled_job(api_connection, job):
        """Fetches scheduled jobs

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        if job.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/schedulemanager/scheduledjobs/' + str(job.pk) + "/", job.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/scheduledjobs/scheduledjobs/', job.get_dict(api_connection))
        return success, returned_data, status_code, error_msg

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
    def get_job_definitions(api_connection):
        """Fetches scheduled jobs and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/jobdefinitions/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_job_definition_by_key(api_connection, pk):
        """Fetches scheduled jobs and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/jobdefinitions/' + str(pk) + "/")
        if json_res is None:
            return None
        return json_res

