import logging
import pandas as pd
logger = logging.getLogger(__name__)

class DsoApi:
    """ Class for DSO

    """

    @staticmethod
    def simulate_dsr_value(api_connection, years=10,
                           capacity=25,current_level=20, max_change=2, invest_grid_mva=5, invest_grid_cost=5000,
                           max_dsr_mva=2,
                           invest_dsr_cost_low=2, invest_dsr_cost_med=5, invest_dsr_cost_high=10,
                           yearly_dsr_cost_low=2, yearly_dsr_cost_med=5, yearly_dsr_cost_high=10,
                           simulation_count=10
                           ):
        """Fetches empty schedule
        """
        payload={
            "years":years,
            "capacity": capacity,
            "current_level": current_level,
            "max_change": max_change,
            "invest_grid_mva": invest_grid_mva,
            "invest_grid_cost": invest_grid_cost,
            "max_dsr_mva":max_dsr_mva,
            "invest_dsr_cost_low":invest_dsr_cost_low,
            "invest_dsr_cost_med":invest_dsr_cost_med,
            "invest_dsr_cost_high":invest_dsr_cost_high,
            "yearly_dsr_cost_low":yearly_dsr_cost_low,
            "yearly_dsr_cost_med":yearly_dsr_cost_med,
            "yearly_dsr_cost_high":yearly_dsr_cost_high,
            "simulation_count":simulation_count
        }
        json_res = api_connection.exec_post_url('/api/riskmanager/grid/simulatedsr/', payload)
        if json_res is None:
            return None
        return json_res
