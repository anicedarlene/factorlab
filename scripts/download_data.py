import duckdb
from factorlab.data import update_prices
from factorlab.universe import load_universe

con = duckdb.connect(
    "factorlab.duckdb",
    config = {"storage_compatibility_version: v1.5.0"}
)

if __name__ == "__main__":
    universe = load_universe()
    print(f"Universe: {len(universe)} tickers")
    update_prices(universe["ticker"].tolist())