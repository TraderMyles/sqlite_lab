from __future__ import annotations
import argparse
from common.db import query_df
from tabulate import tabulate

SQL = """
SELECT strftime('%Y-%m', e.tx_date) AS ym,
       c.name AS category,
       ROUND(SUM(e.amount_cents)/100.0, 2) AS amount
FROM expenses e
JOIN categories c USING(category_id)
WHERE e.tx_date >= date(? || '-01')
  AND e.tx_date <  date(? || '-01','+1 month')
GROUP BY ym, c.name
ORDER BY amount DESC;
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("year_month", help="YYYY-MM")
    args = ap.parse_args()
    ym = args.year_month
    df = query_df(SQL, (ym, ym))
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))

if __name__ == "__main__":
    main()
