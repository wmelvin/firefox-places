#!/usr/bin/env python3

import sys
from pathlib import Path

from html5lib.html5parser import HTMLParser, ParseError

#  Note: When a ParseError occurs, the error messages do not give much
#  context.  Running the tidy (http://www.html-tidy.org/) console
#  application separately on a file that will not parse can provide
#  clues to what needs fixed.


def check_html(file_name, expect_footer):
    print(f"\nParsing '{file_name}'")

    html = Path(file_name).read_text()

    parser = HTMLParser(strict=True)
    # parser = html5lib.HTMLParser()

    try:
        document = parser.parse(html)
    except ParseError as e:
        print(f"  ERROR: {e}")
        return False

    if not expect_footer:
        return True

    check = document.findall(".//*[@id='footer']")
    if len(check) == 1:
        return True
    print('  ERROR: Element not found with id="footer".')
    return False


def main(argv):
    if len(argv) == 2:  # noqa: PLR2004
        #  Can take one argument that is the path containing HTML files.
        check_path = Path(argv[1])
        if not check_path.exists():
            print(f"Path not found: '{check_path}'")
            return 1
    else:
        check_path = Path.cwd() / "output"

    html_files = list(check_path.glob("**/*.html"))

    if len(html_files) == 0:
        print(f"No files found matching *.html in '{check_path}'")
        return 0

    html_files.sort()
    any_errors = False

    for file in html_files:
        if check_html(file, expect_footer=True):
            print("  Ok")
        else:
            any_errors = True

    if any_errors:
        print("\nERRORS FOUND: Review console output.\n")
    else:
        print("\nAll files parsed successfully.\n")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
