from __future__ import annotations
import argparse
from common.db import get_conn
from common.utils import today_iso

def ensure_tag(conn, name: str) -> int:
    conn.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (name,))
    row = conn.execute("SELECT tag_id FROM tags WHERE name=?", (name,)).fetchone()
    return int(row[0])

def create_entry(entry_date: str, title: str, content: str, tags_csv: str | None):
    from common.db import get_conn  # local import just to be explicit
    with get_conn() as conn:
        # 1) insert entry
        cur = conn.execute(
            "INSERT INTO entries(entry_date, title, content) VALUES (?, ?, ?)",
            (entry_date, title, content),
        )
        entry_id = int(cur.lastrowid)

        # 2) tags
        if tags_csv:
            for raw in tags_csv.split(","):
                tag = raw.strip()
                if not tag:
                    continue
                tag_id = ensure_tag(conn, tag)
                conn.execute(
                    "INSERT OR IGNORE INTO entry_tags(entry_id, tag_id) VALUES (?, ?)",
                    (entry_id, tag_id),
                )
    print(f"Saved entry #{entry_id}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=today_iso(), help="YYYY-MM-DD (default: today)")
    p.add_argument("--title", default="")
    p.add_argument("--content", required=True)
    p.add_argument("--tags", default="", help="comma-separated, e.g. clarity,work")
    a = p.parse_args()
    create_entry(a.date, a.title, a.content, a.tags)

if __name__ == "__main__":
    main()
