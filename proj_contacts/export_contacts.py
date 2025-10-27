from __future__ import annotations
import argparse
from pathlib import Path
from common.db import query_df

SQL = """
SELECT
  c.contact_id,
  c.full_name,
  c.email,
  c.phone,
  c.company,
  c.created_at,
  IFNULL(nx.note_count, 0)     AS note_count,
  nx.last_note_date,
  nx.last_note_title,
  nx.last_note_preview
FROM contacts c
LEFT JOIN (
  SELECT
    n1.contact_id,
    COUNT(*) AS note_count,
    MAX(n1.note_date) AS last_note_date,
    /* latest title for that contact */
    (SELECT n2.title
     FROM notes n2
     WHERE n2.contact_id = n1.contact_id
     ORDER BY n2.note_date DESC, n2.note_id DESC
     LIMIT 1) AS last_note_title,
    /* latest body (single-line preview, 120 chars) */
    (SELECT substr(replace(replace(n3.body, char(10), ' '), char(13), ' '), 1, 120)
     FROM notes n3
     WHERE n3.contact_id = n1.contact_id
     ORDER BY n3.note_date DESC, n3.note_id DESC
     LIMIT 1) AS last_note_preview
  FROM notes n1
  GROUP BY n1.contact_id
) nx ON nx.contact_id = c.contact_id
ORDER BY c.full_name COLLATE NOCASE;
"""

def export_csv(out_path: str):
    df = query_df(SQL)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Exported contacts -> {out_path}")

def export_md(out_path: str):
    df = query_df(SQL)
    lines = ["# Contacts Export\n"]
    for _, r in df.iterrows():
        lines.append(f"## {r['full_name']}")
        meta = []
        if r["email"]:  meta.append(f"**Email:** {r['email']}")
        if r["phone"]:  meta.append(f"**Phone:** {r['phone']}")
        if r["company"]:meta.append(f"**Company:** {r['company']}")
        meta.append(f"**Notes:** {int(r['note_count'])}")
        if r["last_note_date"]:
            meta.append(f"**Latest:** {r['last_note_date']} — {r['last_note_title'] or ''}")
            if r["last_note_preview"]:
                meta.append(f"> {r['last_note_preview']}")
        lines.append("\n".join(meta) + "\n")
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"Exported contacts (Markdown) -> {out_path}")

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
