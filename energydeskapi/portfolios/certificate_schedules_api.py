import json
import logging
import pandas as pd


logger = logging.getLogger(__name__)
#  Change

class CertificateSchedule():
    def __init__(self):
        self.pk=0
        self.certificate_contract = None # which is an url
        self.price = None
        self.quantity = None
        self.production_from = None
        self.production_until = None
        self.settlement_date = None
        self.delivery_date = None
        self.flexible_delivery = None
    def get_dict(self):
        dict = {}
        dict['pk']=self.pk
        if self.certificate_contract is not None: dict['certificate_contract'] = self.certificate_contract
        if self.price is not None: dict['price'] = self.price
        if self.quantity is not None: dict['quantity'] = self.quantity
        if self.production_from is not None: dict['production_from'] = self.production_from
        if self.production_until is not None: dict['production_until'] = self.production_until
        if self.settlement_date is not None: dict['settlement_date'] = self.settlement_date
        if self.delivery_date is not None: dict['delivery_date'] = self.delivery_date
        if self.flexible_delivery is not None: dict['flexible_delivery'] = self.flexible_delivery
        return dict

class CertificateSchedulesApi:
    """Class for certificate schedules

      """



    @staticmethod
    def get_certificate_schedules(api_connection, parameters={}):
        """Fetches all certificate schedules

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        """
        logger.info("Fetching certificate schedules")
        json_res = api_connection.exec_get_url('/api/portfoliomanager/certificateschedules/', parameters)
        return json_res

    @staticmethod
    def get_certificate_schedule(api_connection, pk: int):
        """Fetches a specific certificate schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: the id of the schedule that must be loaded
        :type pk: int, required
        """
        logger.info(f"Fetching certificate schedule {pk}")
        json_res = api_connection.exec_get_url(f"/api/portfoliomanager/certificateschedules/{pk}/")
        return json_res


    @staticmethod
    def get_certificate_schedules_of_certificate(api_connection, certificate_id: int, additional_parameters={}):
        """Fetches all schedules for a certain certificate

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param certificate_id: the certificate that owns the schedules
        :type certificate_id: int, required
        """
        logger.info(f"Fetching certificate schedules of certificate {certificate_id}")
        parameters = {
            "certificate_contract__id": str(certificate_id)
        } | additional_parameters
        json_res = api_connection.exec_get_url('/api/portfoliomanager/certificateschedules/', parameters)
        return json_res

    @staticmethod
    def register_certificate_schedule(api_connection, schedule: CertificateSchedule):
        """Registers certificate schedules

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param schedule: schedule to register
        :type schedule: CertificateSchedule, required
        """
        logger.info(f"Registering certificate schedule")
        payload=schedule.get_dict()
        success, json_res, status_code, error_msg=api_connection.exec_post_url('/api/portfoliomanager/certificateschedules/', payload)
        if json_res is None:
            logger.error(f"Problems registering certificate schedule {payload}")
        else:
           logger.info(f"Certificate schedule registered {payload}")
        return success, json_res, status_code, error_msg

    @staticmethod
    def update_certificate_schedule(api_connection, schedule: CertificateSchedule):
        """Update certificate schedules

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param schedule: schedule to update
        :type schedule: CertificateSchedule, required
        """
        logger.info(f"Updating certificate schedule {schedule.pk}")
        payload=schedule.get_dict()
        success, json_res, status_code, error_msg=api_connection.exec_patch_url(f"/api/portfoliomanager/certificateschedules/{schedule.pk}/", payload)
        if json_res is None:
            logger.error(f"Problems updating certificate schedule {payload}")
        else:
            logger.info(f"Certificate schedule updated {payload}")
        return success, json_res, status_code, error_msg

    @staticmethod
    def delete_certificate_schedule(api_connection, pk: int):
        """Deletes a certificate schedule

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param pk: the id of the schedule that must be deleted
        :type pk: int, required
        """
        success, returned_data, status_code, error_msg = api_connection.exec_delete_url(f"/api/portfoliomanager/certificateschedules/{pk}/")
        return success, returned_data, status_code, error_msg

    @staticmethod
    def get_certificate_contract_url(api_connection, certificate_contract_pk: int) -> str:
        """Certificate url from key
        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param certificate_contract_pk: the certificate contract id
        :type certificate_contract_pk: integer, required
        """

        return f"{api_connection.get_base_url()}/api/portfoliomanager/certificatecontracts/{certificate_contract_pk}/"
