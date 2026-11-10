import yfinance as yf

df = yf.download("AAPL", start="2020-01-01", auto_adjust=True)

print(df.head())
print()
print("Rows:", len(df))
print("Date range:", df.index.min().date(), "to", df.index.max().date())