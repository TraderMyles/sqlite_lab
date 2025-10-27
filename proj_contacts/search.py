from __future__ import annotations
import argparse
from common.db import query_df
from tabulate import tabulate

def search_contacts(q: str):
    sql = """
    SELECT contact_id, full_name, email, phone, company, created_at
    FROM contacts
    WHERE (? = '' OR full_name LIKE ? OR email LIKE ? OR phone LIKE ? OR company LIKE ?)
    ORDER BY full_name
    """
    like = f"%{q}%"
    df = query_df(sql, (q, like, like, like, like))
    return df

def search_notes(q: str, email: str | None):
    base = """
    SELECT n.note_id, n.note_date, c.full_name, c.email, COALESCE(n.title,'') AS title,
           substr(replace(replace(n.body, char(10), ' '), char(13), ' '), 1, 140) AS preview
    FROM notes n
    JOIN contacts c ON c.contact_id = n.contact_id
    WHERE 1=1
    """
    params = []
    if q:
        base += " AND (n.title LIKE ? OR n.body LIKE ?)"
        like = f"%{q}%"; params += [like, like]
    if email:
        base += " AND c.email = ?"
        params.append(email)
    base += " ORDER BY n.note_date DESC, n.note_id DESC"
    return query_df(base, tuple(params))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", default="", help="search text for contacts/notes")
    ap.add_argument("--notes", action="store_true", help="search notes instead of contacts")
    ap.add_argument("--email", default="", help="filter notes by contact email")
    args = ap.parse_args()

    if args.notes:
        df = search_notes(args.q, args.email or None)
    else:
        df = search_contacts(args.q)

    if df.empty:
        print("(no matches)")
    else:
        print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))

if __name__ == "__main__":
    main()
