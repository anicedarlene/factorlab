from factorlab.config import DB_PATH
from factorlab.data import get_connection
from factorlab.universe import load_universe

print("Database file:", DB_PATH, "| exists:", DB_PATH.exists())

con = get_connection()
universe = load_universe()

stored = con.execute("""
    SELECT ticker, COUNT(*) AS n_days, MIN(date) AS first_date, MAX(date) AS last_date
    FROM prices GROUP BY ticker
""").fetchdf()

missing = sorted(set(universe["ticker"]) - set(stored["ticker"]))
extra = sorted(set(stored["ticker"]) - set(universe["ticker"]))

print(f"Universe: {len(universe)} | Stored: {len(stored)} | Missing: {len(missing)}")
print("Missing tickers:", missing)
print("Stored but not in universe:", extra)
print(con.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM prices").fetchone())
print("Fewest days of history:")
print(stored.sort_values("n_days").head(10))