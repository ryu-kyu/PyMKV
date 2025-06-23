import argparse, urllib3
import pandas as pd

from io import StringIO
from typing import List, Optional
from urllib3 import util
from bs4 import BeautifulSoup


HTTP = urllib3.PoolManager()


def parse_args(raw_args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape episodes from Wikipedia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Wikipedia URL to scrape from",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--table-heading",
        type=str,
        help="Heading from Wikipedia that contains the table of episodes to extract from",
        required=True,
    )
    parser.add_argument(
        "--from-html-file",
        type=str,
        help="Path to HTML file (used for testing and debugging)",
        required=False,
        default=None,
    )

    parsed_args = parser.parse_args(raw_args)
    return parsed_args


def parse_html(html: str, search_heading: str) -> List[str]:
    """
    Parse HTML for episode names in a given heading section.
    :param html: HTML content as a string
    :param search_heading: Name of the heading to look under
    :return: List of episode names
    """
    episodes: List[str] = []
    soup = BeautifulSoup(html, "html.parser")

    # Locate the heading with the season name
    heading = soup.find(
        lambda tag: tag.name != ""
        and tag.name.startswith("h")
        and search_heading in tag.get_text()
    )
    if not heading:
        print("[-] Heading not found.")
        return []

    # Parse the HTML to get the table data
    html_data = StringIO(html)
    try:
        # Assume second table contains episodes
        df = pd.read_html(html_data)[1]  # type: ignore
    except IndexError:
        # Fall back to first table if only one exists
        df = pd.read_html(html_data)[0]  # type: ignore

    # Try to find a column with "Title" in it (case-insensitive)
    title_column = None
    for col in df.columns:
        if "title" in col.lower():
            title_column = col
            break

    # Extract episode names if a title column was found
    if title_column:
        episodes = df[title_column].tolist()
    else:
        print("[-] Title-like column not found in the table.")

    return episodes


def get_html_contents(url: str) -> Optional[str]:
    """
    Use GET request to retrieve html contents from URL
    :param url: url string
    :return: html body on success
    """
    parsed_url = util.parse_url(url)
    if parsed_url.hostname != "en.wikipedia.org":
        return

    response = HTTP.request("GET", url)

    if response.status != 200:
        print(f"[-] GET request returned status: {response.status}")
        return

    return str(response.data)


def run(raw_args: Optional[List[str]] = None) -> None:
    args = parse_args(raw_args)

    html = None
    if args.from_html_file is None:
        if args.url is None:
            print("[-] Must supply url with (--url) flag")
        html = get_html_contents(args.url)
    else:
        with open(args.from_html_file, "r") as f:
            html = f.read()
    if html is None:
        print(f"[-] Failed to get html contents from: {args.url}")
        return
    episodes = parse_html(html, args.table_heading)
    print(episodes)
    return


if __name__ == "__main__":
    run()
