import numpy as np
import pandas as pd

from factorlab.engine import quintile_weights, run_backtest

def make_returns(n_days=1000, n_stocks=100, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n_days)
    cols = [f"S{i}" for i in range(n_stocks)]
    return pd.DataFrame(rng.normal(0, 0.01, (n_days, n_stocks)), index=idx, columns=cols)

def test_weights_are_dollar_neutral_with_unit_exposure():
    w = quintile_weights(make_returns())
    assert np.allclose(w.sum(axis=1), 0.0)
    assert np.allclose(w.abs().sum(axis=1), 1.0)

def test_engine_does_not_profit_from_same_day_returns():
    """Planted answer: the signal IS today's return. Without a lag this would print money;
    with the one-day lag it should earn roughly nothing."""
    returns = make_returns()
    res = run_backtest(returns, returns, cost_bps=0.0)
    assert abs(res["gross"].mean()) < 5e-4

def test_planted_signal_is_detectable_without_lag():
    """Makes sure the test above has teeth: with no lag, the same signal earns a lot."""
    returns = make_returns()
    unlagged = (quintile_weights(returns) * returns).sum(axis=1).mean()
    assert unlagged > 5e-3