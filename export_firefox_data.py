#!/usr/bin/env python3


import argparse
import sqlite3
import sys
from collections import namedtuple
from pathlib import Path
from datetime import datetime
from textwrap import dedent
from textwrap import indent


Bookmark = namedtuple("Bookmark", "title, url, parent_path")

outpath = Path.cwd() / "output"


def limited(value):
    s = str(value)
    if len(s) <= 180:
        return s
    else:
        return s[:177] + "..."


def html_style():
    s = """
        body {
            font-family: sans-serif;
            padding: 2rem;
        }
        .bookmark-path {
            /* color: #258d25; */
            color: gray;
        }
        .bookmark-title {
            /* color: #7a361f; */
            color: black;
        }
    """
    return s.lstrip("\n").rstrip()


def html_head(title):
    return dedent(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>{0}</title>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <style>
        {1}
            </style>
        </head>
        <body>
        <h1>{0}</h1>
        <ul>
        """
    ).format(title, html_style())


def html_tail():
    return dedent(
        """
        </ul>
        <p>&nbsp;</p>
        <hr>
        </body>
        </html>
        """
    )


def write_history_csv(args, con):
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

    cur = con.cursor()
    cur.execute(sql)

    rows = cur.fetchall()

    file_name = outpath / f"{args.output_prefix}-history.csv"

    print(f"Writing '{file_name}'")
    with open(file_name, "w") as f:
        f.write("url,title,host,visit_count,frecency,visit_date\n")
        for row in rows:
            url = limited(row[0])

            title = limited(str(row[1]).replace('"', "'"))

            #  Use slicing to reverse string [begin:end:step].
            host = row[2][::-1]

            count = row[3]

            frecency = row[4]

            #  The date values in the table are in microseconds since
            #  the Unix epoch. Convert to seconds.
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


def write_bookmarks_csv(args, con):
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

    cur = con.cursor()
    cur.execute(sql)

    rows = cur.fetchall()

    file_name = outpath / f"{args.output_prefix}-bookmarks.csv"

    print(f"Writing '{file_name}'")
    with open(file_name, "w") as f:
        f.write("parent_title,bookmark_title,url\n")
        for row in rows:
            f.write(
                '"{0}","{1}","{2}"{3}'.format(row[0], row[1], row[2], "\n")
            )


def write_bookmarks_html(args, con):
    sql = dedent(
        """
        SELECT
            p.title,
            a.title,
            b.url
        FROM (moz_bookmarks a JOIN moz_places b ON b.id = a.fk)
        JOIN moz_bookmarks p ON p.id = a.parent
        ORDER BY p.title, a.title
        """
    )

    cur = con.cursor()
    cur.execute(sql)

    rows = cur.fetchall()

    file_name = outpath / f"{args.output_prefix}-bookmarks.html"

    print(f"Writing '{file_name}'")
    with open(file_name, "w") as f:

        f.write(html_head("Bookmarks"))
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


def write_frecency_csv(args, con):

    sql = dedent(
        """
        SELECT DISTINCT
            url,
            title,
            frecency
        FROM moz_places
        ORDER BY frecency DESC
        """
    )

    cur = con.cursor()
    cur.execute(sql)

    rows = cur.fetchall()

    file_name = outpath / f"{args.output_prefix}-frecency.csv"

    print(f"Writing '{file_name}'")
    with open(file_name, "w") as f:
        f.write("url,title,frecency\n")
        for row in rows:
            f.write(
                '"{0}","{1}","{2}"{3}'.format(
                    limited(row[0]), limited(row[1]), row[2], "\n"
                )
            )


def get_parent_path(con, id):
    cur = con.cursor()

    depth = 0
    parent_id = id
    parent_path = "/"
    while 0 < parent_id:
        #  It appears that the root always has id=0. If that is not the case
        #  this max-depth check (99 seems like a good arbitrary value) will
        #  prevent an infinate loop.
        depth += 1
        assert depth < 99

        sql = (
            "SELECT parent, title FROM moz_bookmarks WHERE id = {0}"
        ).format(parent_id)

        cur.execute(sql)
        rows = cur.fetchall()
        assert len(rows) == 1

        parent_id = rows[0][0]
        if 0 < parent_id:
            parent_path = f"/{rows[0][1]}{parent_path}"

    return parent_path


def get_bookmarks(con):
    sql = dedent(
        """
        SELECT
            a.title,
            b.url,
            a.parent
        FROM
            moz_bookmarks a
        JOIN moz_places b
        ON b.id = a.fk
        """
    )
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    bmks = []
    for row in rows:
        title = row[0]
        url = row[1]
        parent_id = row[2]
        if title is None:
            title = f"({url})"
        bmks.append(Bookmark(title, url, get_parent_path(con, parent_id)))
    bmks.sort(key=lambda item: item.parent_path + item.title)
    return bmks


# def write_github_links_html(args, con):
#     sql = dedent(
#         """
#         SELECT
#             a.title,
#             b.url,
#             a.parent
#         FROM
#             moz_bookmarks a
#         JOIN moz_places b ON b.id = a.fk
#         WHERE b.url like 'https://github.com/%'
#         ORDER BY a.title
#         """
#     )

#     cur = con.cursor()
#     cur.execute(sql)

#     rows = cur.fetchall()

#     bmks = []
#     for row in rows:
#         #  Append as tuple(parent_path, title, url)
#         bmks.append(
#             (get_parent_path(con, row[2]), row[0], row[1])
#         )
#     #  Sort by parent_path, title.
#     bmks.sort(key=lambda item: item[0] + item[1])

#     file_name = outpath / f"{args.output_prefix}-github-links.html"

#     print(f"Writing '{file_name}'")
#     with open(file_name, "w") as f:
#         f.write(html_head("Bookmarks/GitHub"))
#         for bmk in bmks:
#             parent_path = bmk[0]
#             title = limited(ascii(bmk[1]))
#             url = bmk[2]
#             s = dedent(
#                 """
#                     <li>
#                         <p>{0}<br />
#                         <b>{1}</b><br />
#                         <a target="_blank" href="{2}">{2}</a></p>
#                     </li>
#                     """
#             ).format(parent_path, title, url)
#             f.write(indent(s, " " * 8))
#         f.write(html_tail())


def write_github_links_html(args, con):

    file_name = outpath / f"{args.output_prefix}-github-links.html"

    bmks = get_bookmarks(con)

    print(f"Writing '{file_name}'")
    with open(file_name, "w") as f:
        f.write(html_head("Bookmarks/GitHub"))
        for bmk in bmks:
            if bmk.url.startswith('https://github.com/'):
                title = limited(ascii(bmk.title))
                s = dedent(
                    """
                        <li>
                            <p><span class="bookmark-path">{0}</span><br />
                            <span class="bookmark-title">{1}</span><br />
                            <a target="_blank" href="{2}">{2}</a></p>
                        </li>
                        """
                ).format(bmk.parent_path, title, bmk.url)
                f.write(indent(s, " " * 8))
        f.write(html_tail())


def write_frecency_html(args, con):

    sql = dedent(
        """
        SELECT DISTINCT
            url, title, frecency
        FROM moz_places
        ORDER BY frecency DESC
        LIMIT 100
        """
    )

    cur = con.cursor()
    cur.execute(sql)

    rows = cur.fetchall()

    file_name = outpath / f"{args.output_prefix}-recent-links.html"

    print(f"Writing '{file_name}'")
    with open(file_name, "w") as f:
        f.write(html_head("Top 100 Recent/Frequent  Links"))
        for row in rows:
            s = dedent(
                """
                    <li>
                        <p>{1}<br />
                        <a target="_blank" href="{0}">{0}</a></p>
                    </li>
                    """
            ).format(row[0], row[1])
            f.write(indent(s, " " * 8))
        f.write(html_tail())


def get_args(argv):
    ap = argparse.ArgumentParser(
        description="Extracts information from a Firefox places.sqlite file."
    )

    ap.add_argument(
        "places_file",
        action="store",
        help="Path to the places.sqlite file.",
    )

    ap.add_argument(
        "-p",
        "--output-prefix",
        dest="output_prefix",
        default="places",
        action="store",
        help="Name of prefix for output files. Default is 'places'.",
    )

    ap.add_argument(
        "-g",
        "--do-github",
        dest="do_github",
        action="store_true",
        help="Include an output file listing bookmarks to github URLs.",
    )

    return ap.parse_args(argv[1:])


def main(argv):

    args = get_args(argv)

    db_path = Path(args.places_file)

    if db_path.exists():
        print(f"Reading {db_path}")
        con = sqlite3.connect(db_path)
        # cur = con.cursor()

        write_history_csv(args, con)
        write_bookmarks_csv(args, con)
        write_bookmarks_html(args, con)
        write_frecency_csv(args, con)
        write_frecency_html(args, con)
        if args.do_github:
            write_github_links_html(args, con)

        con.close()
    else:
        print(f"ERROR: Cannot find {db_path}")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
