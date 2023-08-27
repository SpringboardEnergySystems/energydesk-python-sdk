from energydeskapi.types.baselines_enum_types import BaselinesModelsEnums, baseline_description

class BaselinesApi:
    """ Class for baselines data
    """
    @staticmethod
    def generate_baselines(api_connection,  num_days=14, baseline_model=BaselinesModelsEnums.WEEKDAYS_PROFILE):
        payload={
            "num_days":num_days,
            "model_name": baseline_description(baseline_model)
        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/baselines/generatebaselines/', payload)
        return json_res


    @staticmethod
    def get_baseline_models(api_connection, parameters={}):
        json_res = api_connection.exec_get_url('/api/baselines/baselinemodeltypes', parameters)
        return json_res
