PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS contacts (
  contact_id INTEGER PRIMARY KEY,
  full_name  TEXT NOT NULL,
  email      TEXT UNIQUE,                -- optional but unique if present
  phone      TEXT,                       -- free-form; you can normalise later
  company    TEXT,
  created_at TEXT NOT NULL DEFAULT (date('now'))
);

CREATE INDEX IF NOT EXISTS idx_contacts_name   ON contacts(full_name);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company);

CREATE TABLE IF NOT EXISTS notes (
  note_id    INTEGER PRIMARY KEY,
  contact_id INTEGER NOT NULL,
  note_date  TEXT NOT NULL,              -- ISO date
  title      TEXT,
  body       TEXT NOT NULL,
  FOREIGN KEY (contact_id) REFERENCES contacts(contact_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notes_date      ON notes(note_date);
CREATE INDEX IF NOT EXISTS idx_notes_contact   ON notes(contact_id);
