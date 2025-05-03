import logging
import pandas as pd
import json

logger = logging.getLogger(__name__)
#  Change

class WeatherApi:
    @staticmethod
    def generate_weather_scenarios(api_connection, parameters):
        success, json_res, status_code, error_msg = api_connection.exec_post_url(
            '/api/weather/generatescenarios/', parameters)
        if json_res is None:
            logger.error("Problems generating weather scenarios " + str(error_msg))
        else:
            logger.info("Weather scenarios generated")
        return success, json_res, status_code, error_msg