import json
import logging
import pandas as pd

logger = logging.getLogger(__name__)
#  Change
class ClearingApi:
    """Class for clearing reports

    """


    @staticmethod
    def upsert_clearing_report(api_connection, clearing_house, clearing_report_type,clearing_report_format,clearing_report_date, report_data):

        logger.info("Storing clearing report")

        payload = {"clearing_house": clearing_house,
                   "clearing_report_type": clearing_report_type,
                   "clearing_report_format": clearing_report_format,
                   "clearing_date": clearing_report_date,
                   "content": report_data}
        success, json_res, status_code, error_msg  = api_connection.exec_post_url('/api/clearing/reports', payload)
        return True


    @staticmethod
    def query_clearing_report_data(api_connection, clearing_house, clearing_report_type, clearing_report_format, from_date, to_date ):
        """Queries clearing data between a set time

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param clearing_house: description...
        :type clearing_house: str, required
        :param clearing_report_type: type of clearing report
        :type clearing_report_type: str, required
        :param from_date: date and time from
        :type from_date: str, required
        :param to_date: date and time to
        :type to_date: str, required
        """
        logger.info("Querying clearing report types")
        crhouse_pk = clearing_house if isinstance(clearing_house, int) else clearing_house.value
        crtype_pk = clearing_report_type if isinstance(clearing_report_type, int) else clearing_report_type.value
        crform_pk = clearing_report_format if isinstance(clearing_report_format, int) else clearing_report_format.value
        payload = {"clearing_house": crhouse_pk,
                   "clearing_report_type": crtype_pk,
                   "clearing_report_format": crform_pk,
                   "from_datetime": from_date,
                   "to_datetime": to_date}
        success, json_res, status_code, error_msg  = api_connection.exec_post_url('/api/clearing/query-clearing-report-data/', payload)
        return True

    @staticmethod
    def perform_reconciliation(api_connection, date):
        """Reconcile internal and external contracts for a given date

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Reconciling contracts")
        payload = {"date": date}
        success, json_res, status_code, error_msg = api_connection.exec_post_url(
            '/api/clearing/perform-reconciliation/', payload)
        return json_res

    @staticmethod
    def get_clearing_report_records(api_connection, parameters={}):
        """Fetches a list of clearing report records

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching clearing report records list")
        json_res = api_connection.exec_get_url('/api/clearing/reports/', parameters)
        if json_res is None:
            return None
        all_record = []
        for rec in json_res['results']:
            records = json.loads(rec['content'])
            for r in records:
                all_record.append(r)
        return all_record

    @staticmethod
    def get_clearing_report_records_embedded(api_connection, parameters={}):
        """Fetches a list of embedded clearing report records

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching embedded clearing report records list")
        json_res = api_connection.exec_get_url('/api/clearing/reports/embedded/', parameters)
        if json_res is None:
            return None
        all_record = []
        for rec in json_res['results']:
            records = json.loads(rec['content'])
            for r in records:
                all_record.append(r)
        return all_record

    @staticmethod
    def get_clearing_report_records_df(api_connection, parameters={}):
        """Fetches a list of embedded clearing report records

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching embedded clearing report records list")
        all_records = ClearingApi.get_clearing_report_records_embedded(api_connection, parameters)
        df = pd.DataFrame(data=all_records)
        return df

    @staticmethod
    def get_clearing_reports(api_connection, parameters={}):
        """Fetches a list of clearing reports

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching clearing reports list")
        json_res = api_connection.exec_get_url('/api/clearing/reports/', parameters)
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_clearing_reports_embedded(api_connection, parameters={}):
        """Fetches a list of embedded clearing reports

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching embedded clearing reports list")
        json_res = api_connection.exec_get_url('/api/clearing/reports/embedded/', parameters)
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_clearing_report_types(api_connection):
        """Fetches a list of clearing report types

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching clearing report types list")
        json_res = api_connection.exec_get_url('/api/clearing/reporttypes/')
        print(json_res)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_reconciled_trades(api_connection, params={}):
        """Fetches reconciled trades

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching reconciled trades")
        json_res = api_connection.exec_get_url('/api/clearing/reconciledtrades/', params)
        if json_res is None:
            return None
        df = pd.DataFrame(data=json_res)
        return df

    @staticmethod
    def get_embedded_reconciled_trades(api_connection, params={}):
        """Fetches reconciled trades

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching reconciled trades")
        json_res = api_connection.exec_get_url('/api/clearing/reconciledtrades/embedded/', params)
        if json_res is None:
            return None
        #df = pd.DataFrame(data=json_res)
        return json_res
    @staticmethod
    def get_clearing_report_type_url(api_connection, key):
        return api_connection.get_base_url() + '/api/clearing/reporttypes/' + str(key) + "/"
    @staticmethod
    def get_clearing_report_format_url(api_connection, key):
        return api_connection.get_base_url() + '/api/clearing/reportformats/' + str(key) + "/"
    @staticmethod
    def get_clearing_report_house_url(api_connection, key):
        return api_connection.get_base_url() + '/api/clearing/reporthouse/' + str(key) + "/"
