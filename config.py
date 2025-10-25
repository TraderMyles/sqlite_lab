import os
from dotenv import load_dotenv

load_dotenv()  # reads .env if present

DB_PATH = os.getenv("DB_PATH", "data/app.db")
