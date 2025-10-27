from pathlib import Path
from common.db import init_db

def main():
    ddl = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    init_db(ddl)
    print("Journal schema created.")

if __name__ == "__main__":
    main()
