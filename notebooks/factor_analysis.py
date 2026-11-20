import pandas as pd

from factorlab.analysis import forward_returns, daily_ic, ic_summary, quintile_returns
from factorlab.data import load_prices
from factorlab.engine import run_backtest
from factorlab.metrics import summary
from factorlab.signals import compute_returns, low_volatility, momentum_12_1, reversal_1m

START = "2016-01-04"
prices = load_prices()
returns = compute_returns(prices)

signals = {
    "momentum_12_1": momentum_12_1(prices),
    "low_volatility": low_volatility(returns),
    "reversal_1m": reversal_1m(prices),
}

for name, sig in signals.items():
    sig = sig.loc[START:]
    print(f"\n########## {name} ##########")

    ics = {f"{h}d": ic_summary(daily_ic(sig, forward_returns(prices, h).loc[START:]).iloc[::h]) for h in (1, 5, 21)}
    print("\nIC by horizon:")
    print(pd.DataFrame(ics))

    print("\nQuintile returns (annualized, Q1 = weakest signal):")
    print(quintile_returns(sig, returns.loc[START:]))

    res = run_backtest(signals[name], returns, rebalance_every=21).loc[START:]
    print("\nLong-short backtest, monthly rebalance:")
    print(summary(res))