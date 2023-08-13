import logging
import pandas as pd
# from energydeskapi.sdk.common_utils import parse_enum_type
import json

logger = logging.getLogger(__name__)


class RiskAiApi:
    """Class for rating API wrapper

    """

    @staticmethod
    def get_accounts_columns(api_connection):
        """Updates crea

        :param api_connection: class with API token for use with API
        :type api_connection: str, required

        """
        # If rated_company[0] is zero, we should send a POST command in stead; and/or use a different function for it
        result = api_connection.exec_get_url('/api/creditrisk/riskgpt/accountscols/')

        if result is None:

            return []
        return result['columns']

    @staticmethod

    def query_riskgpt_accounts(api_connection, question, columns):
        """Updates crea

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param question: Question to ask GPT
        :type question: str, required
        """
        payload={
            "question": question,
            "columns": columns
        }
        print(payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/creditrisk/riskgpt/accountsquest/', payload)
        if success ==False:

            return {'success':False,
                    'answer':error_msg}
        else:
            return {'success':True,
                    'answer':json_res}

