import sys

import logging
from energydeskapi.sdk.common_utils import init_api
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])
import numpy as np
def simulate_mean_temp(df, days):
    temps = []
    for i in range(days):
        temp = np.random.normal(df['Mean Temp (C)'].mean(), df['Mean Temp (C)'].std())
        temps.append(temp)
    return temps

from scipy.stats import t

def test(df):
    params = t.fit(df['Mean Temp (C)'])
    print(params)
    # Generate random numbers from Student's t-distribution
    results = t.rvs(df=params[0], loc=params[1], scale=params[2], size=1000)
    print(results)
    # Generate random numbers from Student's t-distribution
    results = t.rvs(df=params[0], loc=params[1], scale=params[2], size=1000)
    print('degree of freedom = ', params[0])
    print('loc = ', params[1])
    print('scale = ', params[2])

    df.hist(bins=100, density=True, alpha=0.6, color='b', label='Actual returns distribution')

    # Plot histogram of results
    plt.hist(results, bins=100, density=True, alpha=0.6, color='g', label='Simulated Student/t distribution')

    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.title('Actual returns vs. Projections with a Student\'s t-distribution')
    plt.legend(loc='center left')
    plt.grid(True)
    plt.show()

    num_simulations = 1000
    num_days = 200
    last_price=10
    simulation_student_t = pd.DataFrame()
    for x in range(num_simulations):
        count = 0
        # The first price point
        price_series = []
        rtn = t.rvs(df=params[0], loc=params[1], scale=params[2], size=1)[0]
        price = last_price * (1 + rtn)
        price_series.append(price)
        # Create each price path
        for g in range(num_days):
            rtn = t.rvs(df=params[0], loc=params[1], scale=params[2], size=1)[0]
            price = price_series[g] * (1 + rtn)
            price_series.append(price)
        # Save all the possible price paths
        simulation_student_t[x] = price_series
    fig = plt.figure()
    plt.plot(simulation_student_t)
    plt.xlabel('Number of days')
    plt.ylabel('Possible prices')
    plt.axhline(y=last_price, color='b', linestyle='-')
    plt.show()

import pandas as pd
if __name__ == '__main__':
    #pd.set_option('display.max_rows', None)
    api_conn=init_api()

    import kagglehub

    # Download latest version
    path = kagglehub.dataset_download("annbengardt/noway-meteorological-data")

    print("Path to dataset files:", path)
    f=open(path + "/NorwayMeteoDataCompleted.csv","r")
    df=pd.read_csv(f)
    df=df.loc[df['sourceId']=='SN98978']
    df=df[['sourceId','mean(air_temperature P1D)', 'day', 'month', 'year']]
    df=df.dropna()
    df=df.rename(columns={'mean(air_temperature P1D)':'Mean Temp (C)'})
    print(df)
    test(df)
    sys.exit(0)
    #df2=simulate_mean_temp(df, 30)
    #print(df2)

    n_simulations = 1000
    n_days = 30

    results = []
    for i in range(n_simulations):
        temps = simulate_mean_temp(df, n_days)
        results.append(temps)

    results = pd.DataFrame(results)
    sns.lineplot(data=results.T, color='gray', alpha=0.1, legend=False)

    plt.xlabel('Days')
    plt.ylabel('Mean Temperature (C)')
    plt.show()
