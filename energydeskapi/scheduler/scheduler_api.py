import logging
import pandas as pd
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)

@dataclass
class ScheduledJob:
    pk: int
    job_definition_pk: int
    crontab: str
    dynamic_parameter: str
    is_active: bool

    def get_dict(self, api_conn):
        dict = {'pk':self.pk}
        if self.crontab is not None: dict['crontab'] = self.crontab
        if self.crontab is not None: dict['crontab'] = self.crontab
        if self.dynamic_parameter is not None: dict['dynamic_parameter'] = self.dynamic_parameter
        if self.job_definition_pk is not None: dict['job_definition_pk'] = SchedulerApi.get_job_definition_url(api_conn,self.job_definition_pk)

        return dict
class SchedulerApi:
    """ Class for scheduler

    """
    @staticmethod
    def get_job_definition_url(api_connection, job_definition):
        """Fetches url for company types from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_type_enum: type of company
        :type company_type_enum: str, required
        """

        return api_connection.get_base_url() + '/api/schedulemanager/jobdefinitions/' + str(job_definition) + "/"
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
    def get_scheduled_jobs(api_connection, parameters={}):
        """Fetches scheduled jobs

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobs/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_job_definitions(api_connection, parameters={}):
        """Fetches scheduled jobs and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/jobdefinitions/', parameters)
        if json_res is None:
            return None
        return json_res
    @staticmethod
    def get_scheduled_job_execution(api_connection, job_definition_pk):
        """Fetches scheduled jobs and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        param={'job_definition__pk':job_definition_pk}
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobexecutions/', param)
        if json_res is None:
            return None
        return json_res
