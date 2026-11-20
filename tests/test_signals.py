import numpy as np
import pandas as pd

from factorlab.signals import compute_returns, low_volatility, momentum_12_1, reversal_1m

def make_prices(n_days=400, n_stocks=5):
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2020-01-01", periods=n_days)
    steps = rng.normal(0, 0.01, (n_days, n_stocks))
    return pd.DataFrame(100 * np.exp(np.cumsum(steps, axis=0)), index=idx, columns=list("ABCDE"))

def matches_when_truncated(signal_fn, cutoff_pos=300) -> bool:
    """Compute the signal on all the data and on data cut off at the cutoff date.
    If the value at the cutoff differs, the signal used information from after it."""
    prices = make_prices()
    cutoff = prices.index[cutoff_pos]
    full = signal_fn(prices).loc[cutoff]
    truncated = signal_fn(prices.loc[:cutoff]).loc[cutoff]
    return np.allclose(full.values, truncated.values, equal_nan=True)

def test_momentum_does_not_use_future_data():
    assert matches_when_truncated(momentum_12_1)

def test_low_volatility_does_not_use_future_data():
    #returns are recomputed from the truncated prices, so the whole chain is tested
    assert matches_when_truncated(lambda p: low_volatility(compute_returns(p)))

def test_reversal_does_not_use_future_data():
    assert matches_when_truncated(reversal_1m)

def test_truncation_check_catches_a_leaky_signal():
    """A deliberately leaky signal (looks 5 days ahead) must FAIL the check,
    which proves the check can detect lookahead bias."""
    leaky = lambda p: p.shift(-5) / p - 1
    assert not matches_when_truncated(leaky)