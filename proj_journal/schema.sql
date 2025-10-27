PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS tags (
  tag_id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
  entry_id INTEGER PRIMARY KEY,
  entry_date TEXT NOT NULL,      -- ISO date (YYYY-MM-DD)
  title TEXT,
  content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entry_tags (
  entry_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  PRIMARY KEY (entry_id, tag_id),
  FOREIGN KEY (entry_id) REFERENCES entries(entry_id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id)   REFERENCES tags(tag_id)     ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_entries_date ON entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
