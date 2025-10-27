from __future__ import annotations
import argparse
from common.db import get_conn, query_df

def upsert_contact(full_name: str, email: str | None, phone: str | None, company: str | None):
    with get_conn() as conn:
        if email:
            # Try update by email (unique)
            row = query_df("SELECT contact_id FROM contacts WHERE email=?", (email,))
            if not row.empty:
                cid = int(row.iloc[0]["contact_id"])
                conn.execute("""
                    UPDATE contacts
                       SET full_name = COALESCE(?, full_name),
                           phone     = COALESCE(?, phone),
                           company   = COALESCE(?, company)
                     WHERE contact_id = ?
                """, (full_name or None, phone or None, company or None, cid))
                print(f"Updated contact #{cid} ({email})")
                return cid
        cur = conn.execute(
            "INSERT INTO contacts(full_name, email, phone, company) VALUES (?, ?, ?, ?)",
            (full_name, email or None, phone or None, company or None)
        )
        cid = int(cur.lastrowid)
        print(f"Created contact #{cid}")
        return cid

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--email", default="")
    p.add_argument("--phone", default="")
    p.add_argument("--company", default="")
    a = p.parse_args()
    upsert_contact(a.name.strip(), a.email.strip() or None, a.phone.strip() or None, a.company.strip() or None)

if __name__ == "__main__":
    main()
