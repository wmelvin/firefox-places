#!/usr/bin/env python3

import sqlite3
from pathlib import Path
from datetime import datetime


def limited(value):
    s = str(value)
    if len(s) <= 180:
        return s
    else:
        return s[:177] + "..."


# db_filename = "./data/PC_1/places.sqlite"
# output_prefix = "pc1"

db_filename = "./data/PC_2/places.sqlite"
output_prefix = "pc2"

outpath = Path.cwd() / "output"
outpath_history_places = outpath / f"{output_prefix}-history-places.csv"
outpath_bookmarks = outpath / f"{output_prefix}-bookmarks.csv"
outpath_frecency = outpath / f"{output_prefix}-frecency.csv"

db_path = Path(db_filename)
if db_path.exists():
    print(f"Reading {db_path}")
    connection = sqlite3.connect(db_path)
    c = connection.cursor()

    sql = "SELECT p.url, p.title, p.rev_host, p.visit_count, "
    sql += "p.frecency, h.visit_date "
    sql += "FROM moz_historyvisits h "
    sql += "JOIN moz_places p ON p.id = h.place_id "
    sql += "ORDER BY h.visit_date DESC"

    c.execute(sql)

    print(f"Writing '{outpath_history_places}'")
    with open(outpath_history_places, "w") as f:
        f.write("url,title,host,visit_count,frecency,visit_date\n")
        for row in c.fetchall():
            url = limited(row[0])

            title = limited(str(row[1]).replace('"', "'"))

            # Use slicing to reverse string [begin:end:step].
            host = row[2][::-1]

            count = row[3]

            frecency = row[4]

            # The date values in the table are in microseconds since
            # the Unix epoch. Convert to seconds.
            dts = row[5] / 1000000

            f.write(
                '"{0}","{1}","{2}","{3}","{4}","{5}"{6}'.format(
                    url,
                    title,
                    host,
                    count,
                    frecency,
                    datetime.fromtimestamp(dts),
                    "\n",
                )
            )

    sql = "SELECT p.title, a.title, b.url "
    sql += "FROM (moz_bookmarks a JOIN moz_places b "
    sql += "ON b.id = a.fk) "
    sql += "JOIN moz_bookmarks p ON p.id = a.parent"

    c.execute(sql)

    print(f"Writing '{outpath_bookmarks}'")
    with open(outpath_bookmarks, "w") as f:
        f.write("parent_title,bookmark_title,url\n")
        for row in c.fetchall():
            f.write(
                '"{0}","{1}","{2}"{3}'.format(row[0], row[1], row[2], "\n")
            )

    sql = "SELECT DISTINCT url, title, frecency "
    sql += "FROM moz_places ORDER BY frecency DESC;"

    c.execute(sql)

    print(f"Writing '{outpath_frecency}'")
    with open(outpath_frecency, "w") as f:
        f.write("url,title,frecency\n")
        for row in c.fetchall():
            f.write(
                '"{0}","{1}","{2}"{3}'.format(
                    limited(row[0]), limited(row[1]), row[2], "\n"
                )
            )

    connection.close()
else:
    print(f"ERROR: Cannot find {db_path}")

print("Done.")
