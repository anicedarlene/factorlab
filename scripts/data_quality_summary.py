from factorlab.data import get_connection

con = get_connection()

q = lambda sql: con.execute(sql).fetchone()[0]

print("tickers:", q("SELECT COUNT(DISTINCT ticker) FROM prices"))
print("rows:", q("SELECT COUNT(*) FROM prices"))
print("non-positive or null prices:", q(
    "SELECT COUNT(*) FROM prices WHERE adj_close IS NULL OR adj_close <= 0"))
print("tickers not ending on the last date:", q("""
    SELECT COUNT(*) FROM (SELECT ticker, MAX(date) AS d FROM prices GROUP BY ticker)
    WHERE d < (SELECT MAX(date) FROM prices)"""))
print("daily moves above 40%:", q("""
    WITH r AS (SELECT adj_close / LAG(adj_close) OVER (PARTITION BY ticker ORDER BY date) - 1 AS ret
               FROM prices)
    SELECT COUNT(*) FROM r WHERE ABS(ret) > 0.4"""))
print("tickers with more than 10% zero-return days:", q("""
    WITH r AS (SELECT ticker, adj_close / LAG(adj_close) OVER (PARTITION BY ticker ORDER BY date) - 1 AS ret
               FROM prices)
    SELECT COUNT(*) FROM (
        SELECT ticker FROM r WHERE ret IS NOT NULL
        GROUP BY ticker HAVING AVG(CASE WHEN ret = 0 THEN 1.0 ELSE 0.0 END) > 0.1)"""))