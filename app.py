# app.py
from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, flash
from common.db import get_conn, query_df, execute
from common.utils import parse_amount_to_cents, today_iso

app = Flask(__name__)
app.secret_key = "dev-secret"  # replace in prod

@app.route("/")
def index():
    return render_template("index.html")

# --------------------------
# Expenses (L1-1)
# --------------------------
@app.get("/expenses")
def expenses_list():
    df = query_df("""
        SELECT e.expense_id, e.tx_date, e.merchant, e.note,
               ROUND(e.amount_cents/100.0,2) AS amount, c.name AS category
        FROM expenses e JOIN categories c USING(category_id)
        ORDER BY e.tx_date DESC, e.expense_id DESC
        LIMIT 100
    """)
    rows = df.to_dict("records")
    months = query_df("""
        SELECT strftime('%Y-%m', tx_date) AS ym,
               ROUND(SUM(amount_cents)/100.0,2) AS total
        FROM expenses GROUP BY ym ORDER BY ym DESC
    """).to_dict("records")
    cats = query_df("SELECT name FROM categories ORDER BY name").to_dict("records")
    return render_template("expenses_list.html", rows=rows, months=months, cats=[c["name"] for c in cats])

@app.post("/expenses/add")
def expenses_add():
    date = request.form.get("date") or today_iso()
    amount = request.form.get("amount", "").strip()
    category = request.form.get("category", "").strip()
    merchant = request.form.get("merchant", "").strip()
    note = request.form.get("note", "").strip()

    if not amount or not category:
        flash("Amount and Category are required.", "error")
        return redirect(url_for("expenses_list"))

    # ensure category exists → get id
    execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (category,))
    cat_df = query_df("SELECT category_id FROM categories WHERE name=?", (category,))
    cat_id = int(cat_df.iloc[0]["category_id"])

    cents = parse_amount_to_cents(amount)
    execute("""INSERT INTO expenses(tx_date, amount_cents, category_id, merchant, note)
               VALUES (?, ?, ?, ?, ?)""", (date, cents, cat_id, merchant, note))
    flash("Expense saved.", "ok")
    return redirect(url_for("expenses_list"))

@app.get("/expenses/report/<ym>")
def expenses_report(ym):
    df = query_df("""
        SELECT c.name AS category, ROUND(SUM(e.amount_cents)/100.0,2) AS total
        FROM expenses e JOIN categories c USING(category_id)
        WHERE e.tx_date >= date(? || '-01')
          AND e.tx_date <  date(? || '-01','+1 month')
        GROUP BY c.name
        ORDER BY total DESC
    """, (ym, ym))
    return render_template("expenses_report.html", ym=ym, rows=df.to_dict("records"))

# --------------------------
# Journal (L1-2)
# --------------------------
@app.get("/journal")
def journal_list():
    q = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip()

    sql = """
    SELECT e.entry_id, e.entry_date, IFNULL(e.title,'') AS title,
           substr(replace(replace(e.content, char(10), ' '), char(13), ' '), 1, 140) AS preview,
           IFNULL(GROUP_CONCAT(t.name, ', '), '') AS tags
    FROM entries e
    LEFT JOIN entry_tags et ON et.entry_id = e.entry_id
    LEFT JOIN tags t        ON t.tag_id = et.tag_id
    WHERE 1=1
    """
    params = []
    if q:
        sql += " AND (e.title LIKE ? OR e.content LIKE ?)"
        like = f"%{q}%"; params += [like, like]
    if tag:
        sql += " AND e.entry_id IN (SELECT entry_id FROM entry_tags et2 JOIN tags t2 ON t2.tag_id=et2.tag_id WHERE t2.name=?)"
        params.append(tag)

    sql += " GROUP BY e.entry_id ORDER BY e.entry_date DESC, e.entry_id DESC LIMIT 200"
    rows = query_df(sql, tuple(params)).to_dict("records")
    all_tags = query_df("SELECT name FROM tags ORDER BY name").to_dict("records")
    return render_template("journal_list.html", rows=rows, q=q, tag=tag, tags=[t["name"] for t in all_tags])

@app.post("/journal/add")
def journal_add():
    entry_date = request.form.get("date") or today_iso()
    title = (request.form.get("title") or "").strip()
    content = (request.form.get("content") or "").strip()
    tags_csv = (request.form.get("tags") or "").strip()

    if not content:
        flash("Content is required.", "error")
        return redirect(url_for("journal_list"))

    with get_conn() as conn:
        cur = conn.execute("INSERT INTO entries(entry_date, title, content) VALUES (?, ?, ?)",
                           (entry_date, title, content))
        entry_id = int(cur.lastrowid)
        if tags_csv:
            for raw in tags_csv.split(","):
                t = raw.strip()
                if not t: continue
                conn.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (t,))
                row = conn.execute("SELECT tag_id FROM tags WHERE name=?", (t,)).fetchone()
                conn.execute("INSERT OR IGNORE INTO entry_tags(entry_id, tag_id) VALUES (?, ?)",
                             (entry_id, int(row[0])))
    flash("Entry saved.", "ok")
    return redirect(url_for("journal_list"))

@app.post("/journal/delete/<int:entry_id>")
def journal_delete(entry_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM entries WHERE entry_id=?", (entry_id,))
    flash(f"Deleted entry #{entry_id}.", "ok")
    return redirect(url_for("journal_list"))

# --------------------------
# Contacts (L1-4 variant)
# --------------------------
@app.get("/contacts")
def contacts_list():
    q = request.args.get("q", "").strip()
    like = f"%{q}%"
    df = query_df("""
        SELECT c.contact_id, c.full_name, c.email, c.phone, c.company, c.created_at,
               IFNULL(nc.cnt,0) AS note_count
        FROM contacts c
        LEFT JOIN (SELECT contact_id, COUNT(*) cnt FROM notes GROUP BY contact_id) nc USING(contact_id)
        WHERE (? = '' OR c.full_name LIKE ? OR c.email LIKE ? OR c.phone LIKE ? OR c.company LIKE ?)
        ORDER BY c.full_name
    """, (q, like, like, like, like))
    rows = df.to_dict("records")

    notes = []
    if rows:
        notes = query_df("""
            SELECT n.note_id, n.note_date, c.full_name, c.email, COALESCE(n.title,'') AS title,
                   substr(replace(replace(n.body, char(10), ' '), char(13), ' '),1,140) AS preview
            FROM notes n JOIN contacts c ON c.contact_id = n.contact_id
            ORDER BY n.note_date DESC, n.note_id DESC
            LIMIT 50
        """).to_dict("records")
    return render_template("contacts_list.html", rows=rows, notes=notes, q=q)

@app.post("/contacts/add")
def contacts_add():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip() or None
    phone = request.form.get("phone", "").strip() or None
    company = request.form.get("company", "").strip() or None
    if not name:
        flash("Name is required.", "error")
        return redirect(url_for("contacts_list"))

    # upsert by email if present
    if email:
        df = query_df("SELECT contact_id FROM contacts WHERE email=?", (email,))
        if not df.empty:
            cid = int(df.iloc[0]["contact_id"])
            execute("""UPDATE contacts SET full_name=?, phone=COALESCE(?,phone), company=COALESCE(?,company)
                       WHERE contact_id=?""", (name, phone, company, cid))
            flash("Contact updated.", "ok")
            return redirect(url_for("contacts_list"))
    execute("INSERT INTO contacts(full_name, email, phone, company) VALUES (?, ?, ?, ?)",
            (name, email, phone, company))
    flash("Contact created.", "ok")
    return redirect(url_for("contacts_list"))

@app.post("/contacts/<int:contact_id>/notes/add")
def contacts_add_note(contact_id):
    note_date = request.form.get("date") or today_iso()
    title = (request.form.get("title") or "").strip()
    body = (request.form.get("body") or "").strip()
    if not body:
        flash("Note body is required.", "error")
        return redirect(url_for("contacts_list"))
    execute("INSERT INTO notes(contact_id, note_date, title, body) VALUES (?, ?, ?, ?)",
            (contact_id, note_date, title, body))
    flash("Note saved.", "ok")
    return redirect(url_for("contacts_list"))

@app.post("/contacts/<int:contact_id>/delete")
def contacts_delete(contact_id):
    execute("DELETE FROM contacts WHERE contact_id=?", (contact_id,))
    flash("Contact deleted (notes removed).", "ok")
    return redirect(url_for("contacts_list"))

if __name__ == "__main__":
    app.run(debug=True)
