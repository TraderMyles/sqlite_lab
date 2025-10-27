from __future__ import annotations
import argparse
from pathlib import Path
from common.db import query_df

SQL = """
SELECT e.entry_id, e.entry_date, e.title, e.content,
       GROUP_CONCAT(t.name, ',') AS tags
FROM entries e
LEFT JOIN entry_tags et ON et.entry_id = e.entry_id
LEFT JOIN tags t ON t.tag_id = et.tag_id
GROUP BY e.entry_id
ORDER BY e.entry_date ASC, e.entry_id ASC
"""

def export_csv(path: str):
    df = query_df(SQL)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"CSV exported -> {path}")

def export_md(path: str):
    df = query_df(SQL)
    lines = []
    for _, r in df.iterrows():
        tags = r["tags"] or ""
        title = (r["title"] or "").strip()
        lines.append(f"## {r['entry_date']} — {title}")
        if tags:
            lines.append(f"*Tags:* {tags}")
        lines.append("")
        lines.append(r["content"])
        lines.append("\n---\n")
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"Markdown exported -> {path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fmt", choices=["csv","md"])
    ap.add_argument("out_path")
    args = ap.parse_args()
    if args.fmt == "csv":
        export_csv(args.out_path)
    else:
        export_md(args.out_path)

if __name__ == "__main__":
    main()
