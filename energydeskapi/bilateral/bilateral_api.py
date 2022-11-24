import logging
logger = logging.getLogger(__name__)

class BilateralApi:
    """Class for price curves

    """

    @staticmethod
    def calculate_contract_price(api_connection ,periods, price_area, currency_code, curve_model):
        """Fetches hourly price curve

        :param api_connection: class with API token for use with API
        :type api_connection: str, required
        :param from_period: period from
        :type from_period: str, required
        :param until_period: period to
        :type until_period: str, required
        :param price_area: price area
        :type price_area: str, required
        :param currency_code: specified currency (NOK, EUR, etc.)
        :type currency_code: str, required
        """
        logger.info("Calculate bilateral price")

        dict_periods=[]
        for p in periods:
            dict_periods.append({
            "period_tag": p[0],
            "contract_date_from":p[1],
            "contract_date_until": p[2],
            })
        qry_payload = {
            "forward_curve":{
                    "price_area": price_area,
                    "currency_code": currency_code,
                    "curve_model":curve_model,
                    },
            "periods":dict_periods,
        }

        #print(qry_payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/bilateral/contractpricer/', qry_payload)
        return success, json_res, status_code, error_msg
