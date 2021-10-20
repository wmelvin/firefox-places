#!/usr/bin/env python3

import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from textwrap import dedent
from textwrap import indent


db_filename = "./data/PC_1_FirefoxData/places.sqlite"
output_prefix = "pc1"

# db_filename = "./data/PC_2/places.sqlite"
# output_prefix = "pc2"

outpath = Path.cwd() / "output"
outpath_history_places = outpath / f"{output_prefix}-history-places.csv"
outpath_bookmarks = outpath / f"{output_prefix}-bookmarks.csv"
outpath_frecency = outpath / f"{output_prefix}-frecency.csv"

outpath_custom = outpath / f"{output_prefix}-github-links.html"


def limited(value):
    s = str(value)
    if len(s) <= 180:
        return s
    else:
        return s[:177] + "..."


def html_head(title):
    return dedent(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>{0}</title>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <link rel="stylesheet" href="style.css" />
        </head>
        <body>
            <h1>{0}</h1>
            <ul>
        """
    ).format(title)


def html_tail():
    return dedent(
        """
        </ul>
        </body>
        </html>
        """
    )


def write_history(cur):
    sql = dedent(
        """
        SELECT
            p.url,
            p.title,
            p.rev_host,
            p.visit_count,
            p.frecency,
            h.visit_date
        FROM
            moz_historyvisits h
        JOIN
            moz_places p ON p.id = h.place_id
        ORDER BY
            h.visit_date DESC
        """
    )

    cur.execute(sql)

    rows = cur.fetchall()

    print(f"Writing '{outpath_history_places}'")
    with open(outpath_history_places, "w") as f:
        f.write("url,title,host,visit_count,frecency,visit_date\n")
        for row in rows:
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


def write_bookmarks(cur):
    sql = dedent(
        """
        SELECT
            p.title,
            a.title,
            b.url
        FROM (moz_bookmarks a JOIN moz_places b ON b.id = a.fk)
        JOIN moz_bookmarks p ON p.id = a.parent
        """
    )

    cur.execute(sql)

    rows = cur.fetchall()

    print(f"Writing '{outpath_bookmarks}'")
    with open(outpath_bookmarks, "w") as f:
        f.write("parent_title,bookmark_title,url\n")
        for row in rows:
            f.write(
                '"{0}","{1}","{2}"{3}'.format(row[0], row[1], row[2], "\n")
            )


def write_frecency(cur):
    # --- Frecency:

    sql = dedent(
        """
        SELECT DISTINCT
            url, title, frecency
        FROM moz_places
        ORDER BY frecency DESC
        """
    )

    cur.execute(sql)

    rows = cur.fetchall()

    print(f"Writing '{outpath_frecency}'")
    with open(outpath_frecency, "w") as f:
        f.write("url,title,frecency\n")
        for row in rows:
            f.write(
                '"{0}","{1}","{2}"{3}'.format(
                    limited(row[0]), limited(row[1]), row[2], "\n"
                )
            )


def write_custom_github(cur):
    # --- 2021-10-01 Custom: GitHub?

    sql = dedent(
        """
        select
            p.title as parent_title,
            a.title,
            b.url
        from
            moz_bookmarks a
        join moz_bookmarks p on p.id = a.parent
        join moz_places b on b.id = a.fk
        where b.url like 'https://github.com/%'
        order by p.title, a.title
        """
    )

    cur.execute(sql)

    rows = cur.fetchall()

    print(f"Writing '{outpath_custom}'")
    with open(outpath_custom, "w") as f:
        f.write(html_head("Bookmarks/GitHub"))
        for row in rows:
            parent_title = limited(row[0])
            title = limited(ascii(row[1]))
            url = row[2]
            s = dedent(
                """
                    <li>
                        <p>{0}<br />
                        <b>{1}</b><br />
                        <a target="_blank" href="{2}">{2}</a></p>
                    </li>
                    """
            ).format(parent_title, title, url)
            f.write(indent(s, " " * 8))
        f.write(html_tail())


def main(argv):
    db_path = Path(db_filename)

    if db_path.exists():
        print(f"Reading {db_path}")
        con = sqlite3.connect(db_path)
        cur = con.cursor()

        write_history(cur)

        write_bookmarks(cur)

        write_frecency(cur)

        #  write_custom_github(cur)

        con.close()
    else:
        print(f"ERROR: Cannot find {db_path}")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
