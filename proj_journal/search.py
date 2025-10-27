from __future__ import annotations
import argparse
from common.db import query_df
from tabulate import tabulate

BASE = """
SELECT e.entry_date, COALESCE(e.title,'') AS title,
       substr(replace(replace(e.content, char(10), ' '), char(13), ' '), 1, 120) AS preview
FROM entries e
LEFT JOIN entry_tags et ON et.entry_id = e.entry_id
LEFT JOIN tags t        ON t.tag_id = et.tag_id
WHERE 1=1
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", default="", help="keyword in title/content")
    ap.add_argument("--tag", default="", help="single tag filter")
    ap.add_argument("--from", dest="date_from", default="", help="YYYY-MM-DD")
    ap.add_argument("--to", dest="date_to", default="", help="YYYY-MM-DD (inclusive)")
    args = ap.parse_args()

    sql = BASE
    params = []

    if args.q:
        sql += " AND (e.title LIKE ? OR e.content LIKE ?)"
        like = f"%{args.q}%"
        params += [like, like]
    if args.tag:
        sql += " AND t.name = ?"
        params.append(args.tag)
    if args.date_from:
        sql += " AND e.entry_date >= ?"
        params.append(args.date_from)
    if args.date_to:
        sql += " AND e.entry_date <= ?"
        params.append(args.date_to)

    sql += " GROUP BY e.entry_id ORDER BY e.entry_date DESC"

    df = query_df(sql, tuple(params))
    if df.empty:
        print("(no matches)")
    else:
        print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))

if __name__ == "__main__":
    main()
