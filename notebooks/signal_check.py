from factorlab.data import load_prices
from factorlab.signals import compute_returns, momentum_12_1

prices = load_prices()
returns = compute_returns(prices)
mom = momentum_12_1(prices)

print("prices shape:", prices.shape)
last = mom.index[-1]
print("last date:", last.date())
print("stocks with a momentum value on the last date:", mom.loc[last].notna().sum())
print("\nTop 5 momentum:\n", mom.loc[last].nlargest(5))
print("\nBottom 5 momentum:\n", mom.loc[last].nsmallest(5))
print("\nFirst date with any momentum value:", mom.dropna(how="all").index[0].date())