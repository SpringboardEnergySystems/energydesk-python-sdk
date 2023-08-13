import logging
import pandas as pd
#from energydeskapi.sdk.common_utils import parse_enum_type
import json
from datetime import datetime
logger = logging.getLogger(__name__)

class LoadStaticMatrices:
    
    @staticmethod
    def get_matrices(api_connection):
        logger.info("Fetching matrices")
        json_res=api_connection.exec_get_url('/api/creditrisk/staticmatrix/')
        if json_res is not None:
            return json_res
        return None


class MatrixApi:
    """
    Class for matrix API wrapper
    """
    @staticmethod
    def update_matrix(api_connection, matrix):
        """Updates matrices

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param user: object of user
        :type user: str, required
        """
         #If rated_company[0] is zero, we should send a POST command in stead; and/or use a different function for it
        success, json_res, status_code, error_msg = api_connection.exec_patch_url('/api/creditrisk/staticmatrix/', matrix)
        if json_res is None:
            logger.error("Problems updating matrix " + str(matrix))
            return False
        else:
            logger.info("Updated matrix")
            return True

    @staticmethod
    def get_matrices(api_connection):
        """Fetching list of companies

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching matrices")
        json_res=api_connection.exec_get_url('/api/creditrisk/staticmatrix/')
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def get_matrix(api_connection, pk):
        """Fetches rated company

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching matrix with key " + str(pk))
        json_res=api_connection.exec_get_url('/api/creditrisk/staticmatrix/' + str(pk) + "/")
        if json_res is not None:
            return json_res
        return None
    
    @staticmethod
    def post_matrix(api_connection, id, payload):
        logger.info("Posting matrix with id " + str(id))
        json_res=api_connection.exec_post_url('/api/creditrisk/staticmatrix/', payload)
        if json_res is not None:
            return json_res
        return None

    @staticmethod
    def post_matrix_from_excel(api_connection, name, file_path):
        context = pd.read_excel(file_path)
        json_data = json.loads(context.to_json(orient="records"))
        data = {
            'name': name,
            'matrix': json_data,
            'updated_by': "admin",
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/creditrisk/staticmatrix/', data)
        if json_res is None:
            logger.error("Problems sending matrix " + str(name))
            return False
        else:
            logger.info("Posted matrix")
            return True