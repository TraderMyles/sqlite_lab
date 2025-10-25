from __future__ import annotations
from datetime import date
import re
import hashlib

def today_iso() -> str:
    return date.today().isoformat()

def parse_amount_to_cents(amount: str | float | int) -> int:
    """Safely convert amounts like '12.34' to 1234 cents."""
    s = str(amount).strip().replace(",", "")
    return int(round(float(s) * 100))

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def norm_desc(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s
