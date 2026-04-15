import argparse
import logging
import re
from datetime import date

from curl_cffi import requests

from models import RaceType

DEFAULT_CRAWL_DELAY = 5


def _get_crawl_delay(base_url: str) -> int:
    """ Grabs the crawl delay from a robots.txt file of a website.
    Defines how long to wait between scraper requests.

    :param base_url: The base url of the site that is being scraped
    :return: Integer representing the recommended delay between requests, in seconds
    """
    robots_txt = requests.get(f"{base_url}/robots.txt")

    crawl_delay_search = re.search(r"Crawl-?Delay[^\d]+(\d*)", robots_txt.text, re.IGNORECASE)

    if crawl_delay_search is None or not crawl_delay_search.group(1):
        logging.log(logging.DEBUG, f"Crawl Delay not found in robots.txt. "
                                     f"Setting to default value of {DEFAULT_CRAWL_DELAY})")
        crawl_delay = DEFAULT_CRAWL_DELAY
    else:
        crawl_delay = crawl_delay_search.group(1)
        logging.log(logging.DEBUG, f"crawl_delay = {crawl_delay}")

    return int(crawl_delay)


def main():
    print("Hello from race-finder!")

    parser = argparse.ArgumentParser(
        prog="RaceFinder",
        description="Tell us what you kind of race you're looking for, and we'll scrape the "
                    "internet to help you find it!"
    )

    parser.add_argument("-r", "--race-type", type=str, help="Type of race that you are interested in running.",
                        choices=[race_type.value for race_type in RaceType], required=True)

    date_group = parser.add_argument_group("date args")

    def valid_date(date_str: str) -> str:
        valid_date_format = "%Y-%m-%d"
        try:
            date.strptime(date_str, valid_date_format)
            return date_str
        except Exception:
            msg = f"Incorrectly formatted date: both start_date and end_date must be in the format {valid_date_format}"
            raise argparse.ArgumentTypeError(msg)

    date_group.add_argument("-s", "--start-date", type=valid_date, help="Start date of the search", required=True)
    date_group.add_argument("-e", "--end-date", type=valid_date, help="End date of the search", required=True)

    args = parser.parse_args()

    print(args.start_date)
    print(args)

    # url_base = "https://runningintheusa.com"
    # path = "/race/list/ny/upcoming"

    # response = requests.get(f"{url_base}{path}", impersonate="chrome120")

    # print(response.text)

    # Make a search on the website using city, state, country and see how you would use each parameter
    # USA:
    #


if __name__ == "__main__":
    main()
