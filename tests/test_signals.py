import numpy as np
import pandas as pd

from factorlab.signals import momentum_12_1


def make_prices(n_days=400, n_stocks=5):
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2020-01-01", periods=n_days)
    steps = rng.normal(0, 0.01, (n_days, n_stocks))
    return pd.DataFrame(100 * np.exp(np.cumsum(steps, axis=0)), index=idx, columns=list("ABCDE"))


def test_momentum_does_not_use_future_data():
    prices = make_prices()
    cutoff = prices.index[300]
    full = momentum_12_1(prices)
    truncated = momentum_12_1(prices.loc[:cutoff])  #data after the cutoff removed
    pd.testing.assert_series_equal(full.loc[cutoff], truncated.loc[cutoff])