from factorlab.data import update_prices
from factorlab.universe import load_universe

if __name__ == "__main__":
    universe = load_universe()
    print(f"Universe: {len(universe)} tickers")
    update_prices(universe["ticker"].tolist())