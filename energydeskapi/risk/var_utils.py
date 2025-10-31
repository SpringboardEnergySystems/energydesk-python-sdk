
import pandas as pd
import numpy as np
# Dataclass to hold both daily and yearly standard deviations
class StandardDeviations:
    def __init__(self, daily: pd.Series, yearly: pd.Series):
        self.daily = daily
        self.yearly = yearly
    # A method to print the standard deviations
    def __str__(self):
        return f"Standard Deviations(Daily:\n{self.daily}\nYearly:\n{self.yearly})"

def extract_standard_deviations_from_covar_matrix(cov_matrix: pd.DataFrame) ->StandardDeviations:
    if cov_matrix is None:
        # Return empty standard deviations
        return StandardDeviations(pd.Series(dtype=float), pd.Series(dtype=float))
    variances = pd.Series(
        np.diag(cov_matrix.to_numpy()),
        index=cov_matrix.columns,
        name='variance'
    )
    # optional: standard deviations per product
    std_dev = np.sqrt(variances)
    std_dev_daily = std_dev
    std_dev_yearly = std_dev * np.sqrt(250)
    return StandardDeviations(std_dev_daily, std_dev_yearly)