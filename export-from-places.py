#!/usr/bin/env python3

import sqlite3
from pathlib import Path
from datetime import datetime


def limited(value):
    s = str(value)
    if len(s) <= 180:
        return s
    else:
        return s[:177] + '...'
            

db_filename = "./data/places.sqlite"

outpath_history_places = Path.cwd() / 'output' / 'history_places.csv'
outpath_bookmarks = Path.cwd() / 'output' / 'bookmarks.csv'
outpath_frecency = Path.cwd() / 'output' / 'frecency.csv'

db_path = Path(db_filename)
if db_path.exists():
    print(f"Reading {db_path}")
    connection = sqlite3.connect(db_path)
    c = connection.cursor()
        
    sql = "SELECT p.url, p.title, p.rev_host, p.visit_count, p.frecency, h.visit_date " 
    sql += "FROM moz_historyvisits h "
    sql += "JOIN moz_places p ON p.id = h.place_id " 
    sql += "ORDER BY h.visit_date DESC"
    
    c.execute(sql)
    
    with open(outpath_history_places, 'w') as f:
        f.write("url,title,host,visit_count,frecency,visit_date\n")
        for row in c.fetchall():
            url = limited(row[0])            
                
            title = limited(str(row[1]).replace('"',"'"))
            
            # Use slicing to reverse string [begin:end:step].
            host = row[2][::-1]
            
            count = row[3]
            
            frecency = row[4]
                
            # The date values in the table are in microseconds since 
            # the Unix epoch. Convert to seconds.
            dts = row[5] / 1000000
            
            f.write('"{0}","{1}","{2}","{3}","{4}","{5}"{6}'.format(
                url,
                title,
                host,
                count,
                frecency,
                datetime.fromtimestamp(dts),
                "\n"
            ))
            
    sql = "SELECT p.title, a.title, b.url FROM (moz_bookmarks a JOIN moz_places b ON b.id = a.fk) JOIN moz_bookmarks p ON p.id = a.parent"
    
    c.execute(sql)
    
    with open(outpath_bookmarks, 'w') as f:
        f.write("parent_title,bookmark_title,url\n")
        for row in c.fetchall():
            f.write('"{0}","{1}","{2}"{3}'.format(
                row[0],
                row[1],
                row[2],
                "\n"
            ))    
            

    sql = "SELECT DISTINCT url, title, frecency FROM moz_places ORDER BY frecency DESC;"
    
    c.execute(sql)
    
    with open(outpath_frecency, 'w') as f:
        f.write("url,title,frecency\n")
        for row in c.fetchall():
            f.write('"{0}","{1}","{2}"{3}'.format(
                limited(row[0]),
                limited(row[1]),
                row[2],
                "\n"
            ))    

    connection.close()
else:
    print(f"ERROR: Cannot find {db_path}")

print("Done.")
