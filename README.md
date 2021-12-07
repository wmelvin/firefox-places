# firefox-places #

## Input ##

Firefox stores data about browsing history and bookmarks in a database file called *places.sqlite* in the [profile](https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data) folder. The **export_firefox_places.py** tool queries that [SQLite](https://sqlite.org/index.html) database and produces a set of output files.

It is probably safer to make a copy of the places.sqlite file, when FireFox is not running, and work with that when running this tool.

## Output ##

The following files are produced:
- PREFIX-bookmarks.csv
- PREFIX-bookmarks.html
- PREFIX-frecency.csv
- PREFIX-github-links.html
- PREFIX-history.csv
- PREFIX-recent-links.html


## Command-Line Usage ##

```
usage: export_firefox_data.py [-h] [-p OUTPUT_PREFIX] [-g] places_file

Extracts information from a Firefox places.sqlite file.

positional arguments:
  places_file           Path to the places.sqlite file.

optional arguments:
  -h, --help            show this help message and exit
  -p OUTPUT_PREFIX, --output-prefix OUTPUT_PREFIX
                        Name of prefix for output files. Default is 'places'.
  -g, --do-github       Include an output file listing bookmarks to github
                        URLs.
```

## Links ##

Python - [sqlite3 DB-API 2.0 interface for SQLite databases](https://docs.python.org/3.8/library/sqlite3.html)


[SQLite As An Application File Format](https://sqlite.org/appfileformat.html)
