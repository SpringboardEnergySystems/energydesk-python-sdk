import pendulum

import logging
import pandas as pd
logger = logging.getLogger(__name__)
class OptimizerInput:
    def __init__(self,optimize_fromdate=pendulum.duration(days=-50), optimize_untildate=pendulum.duration(days=-1),
                 capacity_kwh=200, charging_power_kw=45,dis_charging_power_kw=-45,
                 charging_efficiency=0.95, max_soc=0.9, min_soc=0.1):
        self.capacity_kwh=capacity_kwh
        self.charging_power_kw=charging_power_kw
        self.discharging_power_kw=dis_charging_power_kw
        self.charging_efficiency=charging_efficiency
        self.max_soc=max_soc
        self.min_soc = min_soc
        self.optimize_fromdate=optimize_fromdate
        self.optimize_untildate=optimize_untildate

        self.mainmeter_yearly_kwh=2000000
        self.mainmeter_customer_profile=1

    def get_dict(self):
        dict = {}

        if self.capacity_kwh is not None: dict['capacity_kwh'] = self.capacity_kwh
        if self.charging_power_kw is not None: dict['charging_power_kw'] = self.charging_power_kw
        if self.discharging_power_kw is not None: dict['discharging_power_kw'] = self.discharging_power_kw
        if self.charging_efficiency is not None: dict['charging_efficiency'] = self.charging_efficiency
        if self.max_soc is not None: dict['max_soc'] = self.max_soc
        if self.min_soc is not None: dict['min_soc'] = self.min_soc
        if self.optimize_fromdate is not None: dict['optimize_fromdate'] = str(self.optimize_fromdate)
        if self.optimize_untildate is not None: dict['optimize_untildate'] = str(self.optimize_untildate)

        if self.mainmeter_yearly_kwh is not None: dict['mainmeter_yearly_kwh'] = str(self.mainmeter_yearly_kwh)
        if self.mainmeter_customer_profile is not None: dict['mainmeter_customer_profile'] = str(self.mainmeter_customer_profile)

        return dict

class BatteryOptimizationApi:
    """ Class for assets

    """

    @staticmethod
    def optimize_battery(api_connection, optimizer_input):
        payload = optimizer_input.get_dict()
        print(payload)
        success, json_res, status_code, error_msg = api_connection.exec_post_url('/api/flexoptimizer/optimizebattery/', payload)
        if json_res is None:
            logger.error("Problems optimizing battery " + str(error_msg))
        else:
            logger.info("Battery optimized")
