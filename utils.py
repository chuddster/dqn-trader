import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from stockstats import StockDataFrame as Sdf

# Remove chaining warning
pd.options.mode.chained_assignment = None
# Remove summary printing
pd.options.display.max_rows = None


'''
Tinker Source #1:

a) which features to use
b) time ranges for indicators
'''

main_features = [
    'close',
    'volume'
]

# Check https://pypi.org/project/stockstats/ for more indicators
technical_indicators = [
    'rsi_14',
    'cci_14',
    'dx_14'
]


def get_data(col='close'):
    """ Returns a n x n_step array """
    stock_values = []
    for stock_csv in os.listdir('data/'):
        if(stock_csv.startswith('.')):
            continue
        # Data frame w/ open, close, high, low, volume values and reverse
        df = pd.read_csv('data/{}'.format(stock_csv)).iloc[::-1]

        # Convert to stockdataframe
        stock = Sdf.retype(df)

        for indicator in technical_indicators:
            stock.get(indicator)

        mask = main_features + technical_indicators
        stock_table_with_indicators = stock.dropna(
            how='any').loc[:, mask].to_numpy()
        stock_values.append(stock_table_with_indicators)

    return np.array(stock_values)


'''
Tinker Source #2:

a) which scaler to use
'''


def get_scaler(env, max_profit_factor):
    """ Takes a env and returns a scaler for its observation space """

    low = []
    high = []

    max_price = env.stock_price_history.max(axis=1)

    indicators_max = env.stock_indicators_history.max(axis=1)
    indicators_min = env.stock_indicators_history.min(axis=1)

    max_cash = env.init_invest

    for i in max_price:
        low.append(0)
        high.append(i)
    for i in range(0, len(indicators_max)):
        low.extend(list(indicators_min[i]))
        high.extend(list(indicators_max[i]))

    low.append(0)
    high.append(max_cash)

    scaler = StandardScaler()  # MinMaxScaler or RobustScaler
    scaler.fit([low, high])

    print("Scaler is {}".format(scaler))
    return scaler


def maybe_make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
