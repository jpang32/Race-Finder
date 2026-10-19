# scraper/site_parser.py
"""Site-specific URL building and HTML parsing.

Each supported website gets its own pair of functions here. RaceScraper only
fetches HTML; everything that knows about a particular site's layout lives in
this module.
"""

import re

from bs4 import BeautifulSoup

RUNNING_IN_THE_USA_BASE = "https://runningintheusa.com"


def build_runningintheusa_url(
	state: str,
	start_date: str,
	end_date: str,
	race_type: str,
	url_base: str = RUNNING_IN_THE_USA_BASE,
) -> str:
	# Example URL with location, date, race type filters:
	# https://runningintheusa.com/classic/list/within-50-miles-of-albany-ny/4-1-2026-to-4-30-2026/5k
	# With just the state: https://runningintheusa.com/classic/list/ny/4-1-2026-to-4-30-2026/5k
	return f"{url_base}/classic/list/{state}/{start_date}/{end_date}/{race_type}"


def parse_runningintheusa(html: str) -> list[dict[str, str | None]]:
	"""Extract (date, title, types, location) for each race row in the page."""
	soup = BeautifulSoup(html, "html.parser")
	races = []

	for row in soup.find_all("tr")[1:]:
		cells = row.find_all("td")

		# Skip sub-rows that don't have the expected columns (e.g. "Boston Marathon Qualifier" badges)
		if len(cells) < 4:
			continue

		date = cells[1].find(string=re.compile(r".* \d\d?, \d\d\d\d"))
		title = cells[2].find("b")
		types = cells[2].find(string=re.compile("(.*?) run"))
		location = cells[3].find("b")

		races.append(
			{
				"date": date.strip() if date else None,
				"title": title.get_text(strip=True) if title else None,
				"types": types.strip() if types else None,
				"location": location.get_text(strip=True) if location else None,
			}
		)

	return races
