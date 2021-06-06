#!/usr/bin/env python3

import sqlite3
import csv 
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
    
    #sql = "SELECT p.title, a.title, b.url FROM (moz_bookmarks a JOIN moz_places b ON b.id = a.fk) JOIN moz_bookmarks p ON p.id = a.parent"
    
    sql = "SELECT p.url, p.title, h.visit_date FROM moz_historyvisits h JOIN moz_places p ON p.id = h.place_id"
    
    c.execute(sql)
    
    #for a in c.fetchall():
    #    print(a)  
    
    with open('test2.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(c.fetchall())
    
    connection.close()
else:
    print(f"ERROR: Cannot find {db_path}")

print("Done.")
