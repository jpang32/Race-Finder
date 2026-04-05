import logging
import re

from anthropic import Anthropic
from bs4 import BeautifulSoup
from curl_cffi import requests

from models import RaceQuery

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

    # user_query = input("What races can I help you find today?\n")
    #
    # client = Anthropic()
    #
    # response = client.messages.parse(
    #     model="claude-opus-4-6",
    #     max_tokens=1024,
    #     messages=[{
    #         "role": "user",
    #         "content": user_query
    #     }],
    #     output_format=RaceQuery,
    # )

    url_base = "https://runningintheusa.com"
    path = "/race/list/ny/upcoming"

    response = requests.get(f"{url_base}{path}", impersonate="chrome120")

    print(response.text)

    # Make a search on the website using city, state, country and see how you would use each parameter
    # USA:
    #


if __name__ == "__main__":
    main()
