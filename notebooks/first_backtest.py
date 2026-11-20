from factorlab.data import load_prices
from factorlab.engine import run_backtest
from factorlab.signals import compute_returns, momentum_12_1

prices = load_prices()
returns = compute_returns(prices)

res = run_backtest(momentum_12_1(prices), returns).loc["2016-01-04":]

print(res.describe())
print("mean daily turnover:", round(res.turnover.mean(), 4))
print("cumulative gross:", round((1 + res.gross).prod() - 1, 3))
print("cumulative net:  ", round((1 + res.net).prod() - 1, 3))