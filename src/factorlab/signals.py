import pandas as pd

def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change(fill_method=None)

def momentum_12_1(prices: pd.DataFrame, lookback: int = 252, skip: int = 21) -> pd.DataFrame:
    """Return from t-252 to t-21 trading days: 12-month momentum skipping the last month."""
    return prices.shift(skip) / prices.shift(lookback) - 1

def low_volatility(returns: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    """Negative trailing volatility: calmer stocks score higher."""
    return -returns.rolling(window, min_periods=window).std()

def reversal_1m(prices: pd.DataFrame, window: int = 21) -> pd.DataFrame:
    """Negative past 1-month return: recent losers score higher."""
    return -(prices / prices.shift(window) - 1)