from __future__ import annotations
import argparse
from common.db import get_conn, query_df
from common.utils import today_iso

def get_contact_id(email: str | None, contact_id: int | None) -> int:
    if contact_id:
        return contact_id
    if email:
        df = query_df("SELECT contact_id FROM contacts WHERE email=?", (email,))
        if df.empty:
            raise SystemExit(f"No contact found with email '{email}'")
        return int(df.iloc[0]["contact_id"])
    raise SystemExit("Provide --email or --contact-id")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--email", default="")
    p.add_argument("--contact-id", type=int)
    p.add_argument("--date", default=today_iso())
    p.add_argument("--title", default="")
    p.add_argument("--body", required=True)
    a = p.parse_args()

    cid = get_contact_id(a.email or None, a.contact_id)
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO notes(contact_id, note_date, title, body) VALUES (?, ?, ?, ?)",
            (cid, a.date, a.title, a.body)
        )
        nid = int(cur.lastrowid)
    print(f"Saved note #{nid} for contact #{cid}")

if __name__ == "__main__":
    main()
