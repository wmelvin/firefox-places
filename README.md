# firefox-places

Firefox stores data about browsing history and bookmarks in a *Places database*. That database is in a file named *places.sqlite* in the profile[^1] folder. The **export_firefox_places.py** tool queries that SQLite[^2] database and produces a set of output files. It uses the sqlite3[^3] module in the Python Standard Library to do so.

This command-line tool is not meant to be a general-purpose utility. It serves a specific purpose for the author. Nonetheless, it may also serve as an example for others who want to extract a different set of data from their Places database.

For exploring the Places database, and trying different queries, check out [Datasette](https://pypi.org/project/datasette/) or the [DB Browser for SQLite](https://sqlitebrowser.org/).

## Input

It is probably safer to make a copy of the **places.sqlite** file, when FireFox is not running, and work with that when running this tool.

## Output

The following files are produced:

__*prefix*-bookmarks.csv__ - A listing of *parent_path*, *title*, and *url* in text/csv format.

__*prefix*-bookmarks.html__ - A html file with links to each bookmark *url*.

__*prefix*-frecency.csv__ - A listing of *url*, *title*, and *frecency*[^4] in text/csv format.

__*prefix*-github-links.html__ - A html file listing bookmarks where the *url* points to a GitHub page. This is optional (*-g* switch).

__*prefix*-history.csv__ - A listing of *url*, *title*, *host*, *visit_count*, *frecency*, and *visit_date* in text/csv format.

__*prefix*-recent-links.html__ - A html file listing the "*Top 100 Recent/Frequent Links*."


## Command-Line Usage

```
usage: export_firefox_data.py [-h] [-p OUTPUT_PREFIX] [-g] places_file

Extracts information from a Firefox places.sqlite file.

positional arguments:
  places_file           Path to the places.sqlite file.

optional arguments:
  -h, --help            show this help message and exit
  -p OUTPUT_PREFIX, --output-prefix OUTPUT_PREFIX
                        Name of prefix for output files. Default is 'places'.
  -g, --do-github       Include an output file listing bookmarks for github
                        URLs.
```

## Additional

There is also a tool named **check_html_output.py** in this repository. It was used to verify that the generated HTML files are parsable.

## Reference 

[^1]: Firefox - [Profiles](https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data)

[^2]: [SQLite](https://sqlite.org/index.html), [SQLite As An Application File Format](https://sqlite.org/appfileformat.html)

[^3]: Python - [sqlite3 DB-API 2.0 interface for SQLite databases](https://docs.python.org/3.8/library/sqlite3.html)

[^4]: Firefox - [Frecency](https://firefox-source-docs.mozilla.org/browser/urlbar/nontechnical-overview.html#frecency)
