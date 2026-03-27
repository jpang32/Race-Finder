import os

from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup

from models import RaceQuery

def main():
    print("Hello from race-finder!")

    user_query = input("What races can I help you find today?\n")

    client = Anthropic()

    # response = client.messages.parse(
    #     model="claude-opus-4-6",
    #     max_tokens=1024,
    #     messages=[{
    #         "role": "user",
    #         "content": user_query
    #     }],
    #     output_format=RaceQuery,
    # )

    url = "https://runningintheusa.com/race/find-by-state/"
    response = requests.get(url)

    print(response.text)

    # Make a search on the website using city, state, country and see how you would use each parameter
    # USA:
    #


if __name__ == "__main__":

    main()
