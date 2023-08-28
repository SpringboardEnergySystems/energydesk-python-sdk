from energydeskapi.types.baselines_enum_types import BaselinesModelsEnums, baseline_description
from energydeskapi.types.common_enum_types import period_resolution_key
class BaselinesApi:
    """ Class for baselines data
    """
    @staticmethod
    def generate_baselines(api_connection,  payload):

        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/baselines/generatebaseline/', payload)
        return json_res

    @staticmethod
    def upsert_algorithm_instance(api_connection, payload):
        success, returned_data, status_code, error_msg = api_connection.exec_post_url('/api/baselines/algorithminstances/',payload)
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_baseline_algorithminstances(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/baselines/algorithminstances', parameters)
        return json_res

    @staticmethod
    def get_baseline_algorithms(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/baselines/algorithms', parameters)
        return json_res

    @staticmethod
    def get_baseline_resolutions(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/baselines/resolutions', parameters)
        return json_res

    @staticmethod
    def get_baselines_algorithm_url(api_connection, algorithm_enum):
        """Fetches algo type from url
        """
        atype_pk = algorithm_enum if isinstance(algorithm_enum, int) else algorithm_enum.value
        return api_connection.get_base_url() + '/api/baselines/algorithms/' + str(atype_pk) + "/"
    @staticmethod
    def get_baselines_resolutions_url(api_connection, resolution_enum):
        """Fetches algo type from url
        """
        atype_pk = resolution_enum if isinstance(resolution_enum, int) else period_resolution_key(resolution_enum)
        return api_connection.get_base_url() + '/api/baselines/resolutions/' + str(atype_pk) + "/"