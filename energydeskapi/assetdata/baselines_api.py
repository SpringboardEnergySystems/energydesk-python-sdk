

class BaselinesApi:
    """ Class for baselines data
    """
    @staticmethod
    def generate_baselines(api_connection,  parameters={}):
        payload={
            "assets":assets_list,
            "datatype":"FORECAST"

        }
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/assetdata/query-summed-timeseries/', payload)
        return json_res