#!/usr/bin/env python3

from pathlib import Path

import html5lib


def check_html(file_name):
    print(file_name)

    html = Path(file_name).read_text()

    parser = html5lib.HTMLParser(strict=True)
    # parser = html5lib.HTMLParser()

    document = parser.parse(html)

    check = document.findall(".//*[@id='footer']")
    assert len(check) == 1


def main():
    check_path = Path.cwd() / "output"
    html_files = list(check_path.glob("**/*.html"))
    html_files.sort()
    for file in html_files:
        if "PC_2-" in str(file):
            check_html(file)


if __name__ == "__main__":
    main()
