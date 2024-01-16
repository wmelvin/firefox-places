#!/usr/bin/env python3

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from textwrap import dedent, indent
from typing import NamedTuple

app_name = "export_firefox_data.py"

run_dt = datetime.now()

outpath = Path.cwd() / "output"


class Bookmark(NamedTuple):
    title: str
    url: str
    parent_path: str


bookmarks = []


def limited(value):
    s = str(value)
    if len(s) <= 180:  # noqa: PLR2004
        return s
    return s[:177] + "..."


def html_style():
    s = """
        body { font-family: sans-serif; padding: 2rem; }
        .bookmark-path { color: gray; }
        .bookmark-title { color: black; }
        #footer {
            border-top: 1px solid black;
            font-size: x-small;
            margin-top: 2rem;
        }
    """
    return s.lstrip("\n").rstrip()


def html_head(title):
    return (
        dedent(
            """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="generator" content="{0}">
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <title>{1}</title>
            <style>
        {2}
            </style>
        </head>
        <body>
        <h1>{1}</h1>
        <ul>
        """
        )
        .format(app_name, title, html_style())
        .strip("\n")
    )


def html_tail():
    return dedent(
        """
        </ul>
        <div id="footer">
          Created by {0} at {1}.
        </div>
        </body>
        </html>
        """
    ).format(app_name, run_dt.strftime("%Y-%m-%d %H:%M"))


def htm_txt(text: str) -> str:
    s = text.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    return s.replace(">", "&gt;")


def htm_url(url: str) -> str:
    return url.replace("&", "%26")


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

    outfile = outpath / f"{args.output_prefix}-history.csv"

    print(f"Writing '{outfile}'")
    with outfile.open("w") as f:
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


def get_parent_path(con, bookmark_parent_id):
    cur = con.cursor()

    depth = 0
    parent_id = bookmark_parent_id
    parent_path = "/"
    while parent_id > 0:
        #  It appears that the root always has id=0. If that is not the case
        #  this max-depth check (99 seems like a good arbitrary value) will
        #  prevent an infinate loop.
        depth += 1
        assert depth < 99  # noqa: S101, PLR2004

        sql = (  # noqa: S608
            "SELECT parent, title FROM moz_bookmarks WHERE id = {0}"
        ).format(parent_id)

        cur.execute(sql)
        rows = cur.fetchall()
        assert len(rows) == 1  # noqa: S101

        parent_id = int(rows[0][0])
        if parent_id > 0:
            title = str(rows[0][1])
            parent_path = f"/{title}{parent_path}"

    return parent_path


def get_bookmarks(con):
    if bookmarks:
        return bookmarks

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

    for row in rows:
        url = str(row[1])

        if not url.startswith("http"):
            print(f"SKIP NON-HTTP URL: '{url}'")
            continue

        title = str(row[0])
        parent_id = int(row[2])

        if title is None:
            title = f"({url})"

        bookmarks.append(Bookmark(title, url, get_parent_path(con, parent_id)))

    bookmarks.sort(key=lambda item: item.parent_path + item.title)

    return bookmarks


def write_bookmarks_csv(args, con):
    outfile = outpath / f"{args.output_prefix}-bookmarks.csv"

    bmks = get_bookmarks(con)

    print(f"Writing '{outfile}'")
    with outfile.open("w") as f:
        f.write("parent_path,title,url\n")
        for bmk in bmks:
            f.write('"{0}","{1}","{2}"\n'.format(bmk.parent_path, bmk.title, bmk.url))


def write_bookmarks_html(args, con):
    outfile = outpath / f"{args.output_prefix}-bookmarks.html"

    bmks = get_bookmarks(con)

    print(f"Writing '{outfile}'")
    with outfile.open("w") as f:
        f.write(html_head("Bookmarks"))

        for bmk in bmks:
            title = limited(ascii(bmk.title))
            s = dedent(
                """
                    <li>
                        <p><span class="bookmark-path">{0}</span><br />
                        <span class="bookmark-title">{1}</span><br />
                        <a target="_blank" href=
                        "{2}">
                        {2}</a></p>
                    </li>
                    """
            ).format(htm_txt(bmk.parent_path), htm_txt(title), htm_url(bmk.url))
            f.write(indent(s, " " * 8))
        f.write(html_tail())


def write_github_links_html(args, con):
    outfile = outpath / f"{args.output_prefix}-github-links.html"

    bmks = get_bookmarks(con)

    print(f"Writing '{outfile}'")
    with outfile.open("w") as f:
        f.write(html_head("Bookmarks/GitHub"))
        for bmk in bmks:
            if bmk.url.startswith("https://github.com/"):
                title = limited(ascii(bmk.title))
                s = dedent(
                    """
                        <li>
                            <p><span class="bookmark-path">{0}</span><br />
                            <span class="bookmark-title">{1}</span><br />
                            <a target="_blank" href=
                            "{2}">
                            {2}</a></p>
                        </li>
                        """
                ).format(htm_txt(bmk.parent_path), htm_txt(title), htm_url(bmk.url))
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

    outfile = outpath / f"{args.output_prefix}-frecency.csv"

    print(f"Writing '{outfile}'")
    with outfile.open("w") as f:
        f.write("url,title,frecency\n")
        for row in rows:
            f.write(
                '"{0}","{1}","{2}"{3}'.format(
                    limited(row[0]), limited(row[1]), row[2], "\n"
                )
            )


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

    outfile = outpath / f"{args.output_prefix}-recent-links.html"

    print(f"Writing '{outfile}'")
    with outfile.open("w") as f:
        f.write(html_head("Top 100 Recent/Frequent  Links"))
        for row in rows:
            url = row[0]
            title = row[1]
            if title is None:
                title = f"({url})"
            s = dedent(
                """
                    <li>
                        <p>{1}<br />
                        <a target="_blank" href=
                        "{0}">
                        {0}</a></p>
                    </li>
                    """
            ).format(htm_url(url), htm_txt(title))
            f.write(indent(s, " " * 8))
        f.write(html_tail())


def get_args(arglist=None):
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
        help="Include an output file listing bookmarks for github URLs.",
    )

    return ap.parse_args(arglist)


def main(arglist=None):
    args = get_args(arglist)

    db_path = Path(args.places_file)

    if not db_path.exists():
        print(f"ERROR: Cannot find {db_path}")
        return 1

    print(f"Reading {db_path}")
    con = sqlite3.connect(db_path)

    write_history_csv(args, con)
    write_bookmarks_csv(args, con)
    write_bookmarks_html(args, con)
    write_frecency_csv(args, con)
    write_frecency_html(args, con)
    if args.do_github:
        write_github_links_html(args, con)

    con.close()

    print("Done.")
    return 0


if __name__ == "__main__":
    main()
