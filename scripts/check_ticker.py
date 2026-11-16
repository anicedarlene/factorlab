import sys

from factorlab.data import get_connection

con = get_connection()
for t in sys.argv[1:]:
    print(f"\n=== {t}: zero-return days by year ===")
    print(
        con.execute(
            """
            WITH r AS (
                SELECT date, adj_close,
                       adj_close / LAG(adj_close) OVER (ORDER BY date) - 1 AS ret
                FROM prices WHERE ticker = ?
            )
            SELECT YEAR(date) AS year, COUNT(*) AS n_days,
                   SUM(CASE WHEN ret = 0 THEN 1 ELSE 0 END) AS zero_days,
                   ROUND(MIN(adj_close), 2) AS min_price,
                   ROUND(MAX(adj_close), 2) AS max_price
            FROM r GROUP BY year ORDER BY year
            """,
            [t],
        )
        .fetchdf()
        .to_string(index=False)
    )