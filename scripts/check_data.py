from factorlab.data import get_connection

con = get_connection()


def section(title: str, sql: str) -> None:
    print(f"\n=== {title} ===")
    print(con.execute(sql).fetchdf().to_string(index=False))


section("1. Overview", """
    SELECT COUNT(*) AS n_rows,
           COUNT(DISTINCT ticker) AS n_tickers,
           MIN(date) AS first_date,
           MAX(date) AS last_date
    FROM prices
""")

section("2. Do all tickers end on the same date?", """
    SELECT last_date, COUNT(*) AS n_tickers
    FROM (SELECT ticker, MAX(date) AS last_date FROM prices GROUP BY ticker)
    GROUP BY last_date ORDER BY last_date
""")

section("3. Shortest histories (recent IPOs expected)", """
    SELECT ticker, COUNT(*) AS n_days, MIN(date) AS first_date
    FROM prices GROUP BY ticker ORDER BY n_days LIMIT 10
""")

section("4. Non-positive or missing prices (should be empty)", """
    SELECT * FROM prices
    WHERE adj_close IS NULL OR adj_close <= 0 LIMIT 10
""")

section("5. Missing trading days inside a ticker's own history", """
    WITH cal AS (
        SELECT date FROM prices GROUP BY date HAVING COUNT(*) > 100
    ),
    bounds AS (
        SELECT ticker, MIN(date) AS first_d, MAX(date) AS last_d
        FROM prices GROUP BY ticker
    ),
    expected AS (
        SELECT b.ticker, COUNT(*) AS n_expected
        FROM bounds b JOIN cal c ON c.date BETWEEN b.first_d AND b.last_d
        GROUP BY b.ticker
    ),
    actual AS (
        SELECT ticker, COUNT(*) AS n_actual FROM prices GROUP BY ticker
    )
    SELECT e.ticker, e.n_expected, a.n_actual, e.n_expected - a.n_actual AS missing_days
    FROM expected e JOIN actual a USING (ticker)
    WHERE e.n_expected - a.n_actual > 0
    ORDER BY missing_days DESC LIMIT 15
""")

section("6. Largest daily moves (|return| > 40%), with the next day's return", """
    WITH r AS (
        SELECT ticker, date,
               adj_close / LAG(adj_close) OVER (PARTITION BY ticker ORDER BY date) - 1 AS ret
        FROM prices
    ),
    r2 AS (
        SELECT *, LEAD(ret) OVER (PARTITION BY ticker ORDER BY date) AS next_ret
        FROM r
    )
    SELECT ticker, date, ROUND(ret, 3) AS ret, ROUND(next_ret, 3) AS next_ret
    FROM r2 WHERE ABS(ret) > 0.4
    ORDER BY ABS(ret) DESC LIMIT 20
""")

section("7. Possibly stale prices (share of days with exactly 0% return)", """
    WITH r AS (
        SELECT ticker,
               adj_close / LAG(adj_close) OVER (PARTITION BY ticker ORDER BY date) - 1 AS ret
        FROM prices
    )
    SELECT ticker,
           ROUND(AVG(CASE WHEN ret = 0 THEN 1.0 ELSE 0.0 END), 3) AS share_zero_days,
           COUNT(*) AS n_days
    FROM r WHERE ret IS NOT NULL
    GROUP BY ticker HAVING share_zero_days > 0.1
    ORDER BY share_zero_days DESC LIMIT 10
""")