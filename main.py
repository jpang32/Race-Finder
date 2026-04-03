import os

from anthropic import Anthropic
import logging
import requests
import re
from bs4 import BeautifulSoup

from models import RaceQuery

DEFAULT_CRAWL_DELAY = 5

def main():
    print("Hello from race-finder!")

    user_query = input("What races can I help you find today?\n")

    client = Anthropic()

    response = client.messages.parse(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": user_query
        }],
        output_format=RaceQuery,
    )

    url_base = "https://runningintheusa.com"
    robots_txt = requests.get(f"{url_base}/robots.txt")

    crawl_delay_search = re.search(r"Crawl-?Delay[^\d]+(\d*)", robots_txt.text, re.IGNORECASE)

    if crawl_delay_search is None or not crawl_delay_search.group(1):
        logging.log(logging.DEBUG, f"Crawl Delay not found in robots.txt. "
                                     f"Setting to default value of {DEFAULT_CRAWL_DELAY})")
        crawl_delay = DEFAULT_CRAWL_DELAY
    else:
        crawl_delay = crawl_delay_search.group(1)
        logging.log(logging.DEBUG, f"crawl_delay = {crawl_delay}")



    # Make a search on the website using city, state, country and see how you would use each parameter
    # USA:
    #


if __name__ == "__main__":

    main()
