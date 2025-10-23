import logging
import pandas as pd
from dataclasses import dataclass, asdict, field
from dataclasses import dataclass
from enum import Enum

from energydeskapi.sdk.api_connection import ApiConnection

logger = logging.getLogger(__name__)




@dataclass(frozen=True)
class SchedulerMessage():
    receiver_id: str
    payload: str


class ScheduledJob:
    def __init__(self):
        self.pk = 0
        self.job_definition_pk = 0
        self.crontab = None
        #must be removed
        self.dynamic_parameter = None
        self.dynamic_config = None
        self.is_active = None

    def get_dict(self, api_conn):
        dict = {'pk':self.pk}
        if self.job_definition_pk  != 0: dict['job_definition'] = SchedulerApi.get_job_definition_url(api_conn,self.job_definition_pk)
        if self.crontab is not None: dict['crontab'] = self.crontab
        if self.dynamic_parameter is not None: dict['dynamic_parameter'] = self.dynamic_parameter
        if self.dynamic_config is not None: dict['dynamic_config'] = self.dynamic_config
        if self.is_active is not None: dict['is_active'] = self.is_active
        return dict

class ScheduledJobExecution:
    def __init__(self):
        self.pk = 0
        self.job = None
        self.logtime = None
        self.message = None
        self.taskdone = False
        self.success = False

    def get_dict(self):
        dict = {'pk': self.pk}
        if self.job is not None: dict['job'] = self.job
        if self.logtime is not None: dict['logtime'] = self.logtime
        if self.message is not None: dict['message'] = self.message
        if self.taskdone is not None: dict['taskdone'] = self.taskdone
        if self.success is not None: dict['success'] = self.success

        return dict

class JobDefinition:
    def __init__(self):
        self.pk = 0
        self.description = None
        self.func_name = None
        self.python_module = None
        self.config = None

    def get_dict(self, api_conn):
        dict = {'pk':self.pk}
        if self.description is not None: dict['description'] = self.description
        if self.func_name is not None: dict['func_name'] = self.func_name
        if self.python_module is not None: dict['python_module'] = self.python_module
        if self.config is not None: dict['config'] = self.config
        return dict

class SchedulerApi:
    """ Class for scheduler

    """
    @staticmethod
    def get_job_definition_url(api_connection: ApiConnection, job_definition_pk: int) -> str:
        """Fetches url for company types from enum value

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param company_type_enum: type of company
        :type company_type_enum: str, required
        """

        return api_connection.get_base_url() + '/api/schedulemanager/jobdefinitions/' + str(job_definition_pk) + "/"

    @staticmethod
    def upsert_scheduled_job(api_connection: ApiConnection, job: ScheduledJob):
        """Fetches scheduled jobs

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        if job.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                '/api/schedulemanager/scheduledjobs/' + str(job.pk) + "/", job.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/schedulemanager/scheduledjobs/', job.get_dict(api_connection))
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_scheduled_jobs(api_connection: ApiConnection, parameters: dict={}):
        """Fetches scheduled jobs

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobs/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_scheduled_jobs_df(api_connection: ApiConnection, parameters: dict={}):
        """Fetches scheduled jobs df

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobs/', parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_scheduled_jobs_embedded(api_connection: ApiConnection, parameters: dict={}):
        """Fetches scheduled jobs embedded df

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobs/embedded/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_scheduled_jobs_embedded_df(api_connection: ApiConnection, parameters: dict={}):
        """Fetches scheduled jobs embedded df

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobs/embedded/', parameters)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_scheduled_job(api_connection: ApiConnection, pk: int):
        """Fetches scheduled job by pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobs/' + str(pk) + '/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_scheduled_job_embedded(api_connection: ApiConnection, pk: int):
        """Fetches scheduled job by pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobs/' + str(pk) + '/retrieve_embedded/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_job_definitions(api_connection: ApiConnection, parameters: dict={}):
        """Fetches scheduled jobs and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/jobdefinitions/', parameters)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_job_definition(api_connection: ApiConnection, pk: int):
        """Fetches scheduled job by pk

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        json_res = api_connection.exec_get_url('/api/schedulemanager/jobdefinitions/' + str(pk) + '/')
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upsert_job_definition(api_connection: ApiConnection, job: JobDefinition):
        """Fetches scheduled jobs

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """

        if job.pk > 0:
            success, returned_data, status_code, error_msg = api_connection.exec_patch_url(
                f"/api/schedulemanager/jobdefinitions/{job.pk}/", job.get_dict(api_connection))
        else:
            success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/schedulemanager/jobdefinitions/', job.get_dict(api_connection))
        return success, returned_data, status_code, error_msg


    @staticmethod
    def get_scheduled_job_execution(api_connection: ApiConnection, job_definition_pk: int):
        """Fetches scheduled jobs and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        param={'job__id':job_definition_pk}
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobexecutions/', param)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def get_scheduled_job_execution_embedded(api_connection: ApiConnection, param: dict):
        """Fetches scheduled jobs and displays in a dataframe

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        #param = {'job__id': job_definition_pk}
        json_res = api_connection.exec_get_url('/api/schedulemanager/scheduledjobexecutions/embedded/', param)
        if json_res is None:
            return None
        return json_res

    @staticmethod
    def upload_scheduled_job_execution(api_connection: ApiConnection, execution: ScheduledJobExecution):
        """Uploads scheduled job executions

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        payload = execution.get_dict()

        success, returned_data, status_code, error_msg = api_connection.exec_post_url(
                '/api/schedulemanager/scheduledjobexecutions/', payload)

        return success, returned_data, status_code, error_msg
