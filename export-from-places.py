#!/usr/bin/env python3

import sqlite3
from pathlib import Path

db_filename = "./data/places.sqlite"

db_path = Path(db_filename)
if db_path.exists():
    print(f"Reading {db_path}")
    connection = sqlite3.connect(db_path)
    c = connection.cursor()
    
    #c.execute("SELECT DISTINCT url FROM moz_places")
    #print(c.fetchall())
    
    #sql = "SELECT a.title, b.url FROM moz_bookmarks a JOIN moz_places b ON b.id = a.fk"
    
    sql = "SELECT p.title, a.title, b.url FROM (moz_bookmarks a JOIN moz_places b ON b.id = a.fk) JOIN moz_bookmarks p ON p.id = a.parent"
    
    c.execute(sql)
    for a in c.fetchall():
        print(a)  
    
    
    connection.close()
else:
    print(f"ERROR: Cannot find {db_path}")

print("Done.")
