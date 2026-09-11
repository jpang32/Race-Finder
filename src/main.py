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


def _fetch_race_info(
	url_base: str,
	state: str,
	start_date: str,
	end_date: str,
	race_type: str,
):
	# Example URL with location, date, race type filters:
	# https://runningintheusa.com/classic/list/within-50-miles-of-albany-ny/4-1-2026-to-4-30-2026/5k
	# With just the state: https://runningintheusa.com/classic/list/ny/4-1-2026-to-4-30-2026/5k
	path_base = "classic/list"
	path_params = f"{state}/{start_date}/{end_date}/{race_type}"
	url = f"{url_base}/{path_base}/{path_params}"
	print(f"Fetching: {url}")

	html_content = fetch_page(url)

	soup = BeautifulSoup(html_content, "html.parser")
	race_info_rows = soup.find_all("tr")

	for row in race_info_rows[1:]:
		race_info_cells = row.find_all("td")

		# Skip sub-rows that don't have the expected columns (e.g. "Boston Marathon Qualifier" badges)
		if len(race_info_cells) < 4:
			continue

		# Race Date
		race_date_cell = race_info_cells[1]
		race_date = race_date_cell.find(string=re.compile(r".* \d\d?, \d\d\d\d"))

		# Race Title (and types)
		race_title_cell = race_info_cells[2]
		race_title = race_title_cell.find("b")
		race_types = race_title_cell.find(string=re.compile("(.*?) run"))

		race_title_and_types = f"{race_title} ({race_types})"

		# Race Location
		race_location_cell = race_info_cells[3]
		race_location = race_location_cell.find("b")

		print(race_date, race_title_and_types, race_location)

	return


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
