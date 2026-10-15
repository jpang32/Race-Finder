import argparse
import re
from datetime import date

from bs4 import BeautifulSoup

from models import RaceType
from scraper.scraper import fetch_page


def _parse_args():
	parser = argparse.ArgumentParser(
		prog="RaceFinder",
		description="Tell us what you kind of race you're looking for, and we'll scrape the "
		"internet to help you find it!",
	)

	parser.add_argument(
		"-r",
		"--race-type",
		type=str,
		help="Type of race that you are interested in running.",
		choices=[race_type.value for race_type in RaceType],
		required=True,
	)

	parser.add_argument(
		"-s",
		"--state",
		type=str,
		help="US state of race that you are interested in running.",
	)
	date_group = parser.add_argument_group("date args")

	def valid_date(date_str: str) -> str:
		valid_date_format = "%m-%d-%Y"
		try:
			date.strptime(date_str, valid_date_format)
			return date_str
		except Exception:
			msg = f"Incorrectly formatted date: both start_date and end_date must be in the format {valid_date_format}"
			raise argparse.ArgumentTypeError(msg)

	date_group.add_argument("-b", "--start-date", type=valid_date, help="Start date of the search", required=True)
	date_group.add_argument("-e", "--end-date", type=valid_date, help="End date of the search", required=True)

	return parser.parse_args()

def main():
	print("Hello from race-finder!")

	args = _parse_args()
	state = args.state.lower()
	start_date = args.start_date
	end_date = args.end_date
	race_type = args.race_type

	url_base = "https://runningintheusa.com"

	_fetch_race_info(url_base, state, start_date, end_date, race_type)

	# soup
	# Grab tables
	# Grab the body of the table
	# For each row, grab each the first 3 cells
	# How to iterate through the pages

	# If user
	# Filter on the date column first,
	print()


if __name__ == "__main__":
	main()
