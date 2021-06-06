#!/usr/bin/env python3

import sqlite3
from pathlib import Path

db_filename = "./data/places.sqlite"

db_path = Path(db_filename)
if db_path.exists():
    print(f"Reading {db_path}")
    connection = sqlite3.connect(db_path)
    c = connection.cursor()
    c.execute("SELECT DISTINCT url FROM moz_places")
    print(c.fetchall())
    connection.close()
else:
    print(f"ERROR: Cannot find {db_path}")

print("Done.")
