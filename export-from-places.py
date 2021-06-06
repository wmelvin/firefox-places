#!/usr/bin/env python3

import sqlite3
from pathlib import Path
from datetime import datetime

db_filename = "./data/places.sqlite"

outpath_history_places = Path.cwd() / 'output' / 'history_places.csv'
outpath_bookmarks = Path.cwd() / 'output' / 'bookmarks.csv'

db_path = Path(db_filename)
if db_path.exists():
    print(f"Reading {db_path}")
    connection = sqlite3.connect(db_path)
    c = connection.cursor()
        
    sql = "SELECT p.url, p.title, p.rev_host, p.visit_count, h.visit_date " 
    sql += "FROM moz_historyvisits h "
    sql += "JOIN moz_places p ON p.id = h.place_id " 
    sql += "ORDER BY h.visit_date"
    
    c.execute(sql)
    
    with open(outpath_history_places, 'w') as f:
        f.write("url,title,host,visit_count,visit_date\n")
        for row in c.fetchall():
            url = row[0]
            
            # TODO: Probably don't want to truncate the URL at only 80 chars in final version.
            if len(url) > 80:
                url = url[:77] + '...'
                
            title = row[1]
            
            # Use slicing to reverse string [begin:end:step].
            host = row[2][::-1]
            
            count = row[3]
                
            # The date values in the table are in microseconds since 
            # the Unix epoch. Convert to seconds.
            dts = row[4] / 1000000
            
            f.write('"{0}","{1}","{2}","{3}","{4}"{5}'.format(
                url,
                title,
                host,
                count,
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
    
    connection.close()
else:
    print(f"ERROR: Cannot find {db_path}")

print("Done.")
