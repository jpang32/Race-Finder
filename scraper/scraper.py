# scraper/scraper.py

import json
import logging
import time
from pathlib import Path

import undetected_chromedriver as uc
from curl_cffi import requests as cffi_requests

COOKIE_DIR = Path.home() / ".race-finder"
COOKIE_FILE = COOKIE_DIR / "cookies.json"

# The only cookie needed to pass the Cloudflare challenge
CF_COOKIE_NAME = "cf_clearance"

_CF_WAIT = 6

logger = logging.getLogger(__name__)


class RaceScraper:
	def __init__(self):
		COOKIE_DIR.mkdir(parents=True, exist_ok=True)

	def fetch_page(self, url: str) -> str:
		"""Fetch a page, automatically handling Cloudflare protection.

		Tries curl_cffi with the saved cf_clearance cookie first (fast), and
		falls back to a real browser if there is no cookie or it was rejected.
		"""
		cf_clearance = self._load_cf_clearance()
		if cf_clearance:
			response = cffi_requests.get(url, cookies={CF_COOKIE_NAME: cf_clearance})
			if response.status_code == 200:
				return response.text

		logger.info("Falling back to browser method for %s", url)
		print("Missing or invalid cf_clearance — launching browser to solve Cloudflare challenge...")
		return self._fetch_with_browser(url)

	def _load_cf_clearance(self) -> str | None:
		"""Load the saved cf_clearance value from disk, if any."""
		try:
			return json.loads(COOKIE_FILE.read_text()).get(CF_COOKIE_NAME)
		except FileNotFoundError:
			return None
		except (json.JSONDecodeError, AttributeError, OSError) as e:
			logger.error("Error loading cookies: %s", e)
			return None

	def _fetch_with_browser(self, url: str) -> str:
		"""Use undetected-chromedriver to solve Cloudflare JS challenges.

		Runs in visible (non-headless) mode because Cloudflare reliably detects
		headless Chrome. After passing the challenge, cf_clearance is saved so
		future requests can skip the browser.
		"""
		driver = uc.Chrome(version_main=152)

		try:
			driver.get(url)
			time.sleep(_CF_WAIT)
			html = driver.page_source

			self._save_cf_clearance(driver)

			return html
		finally:
			driver.quit()

	def _save_cf_clearance(self, driver: uc.Chrome):
		"""Persist only the cf_clearance cookie to disk for reuse across runs."""
		cookie = driver.get_cookie(CF_COOKIE_NAME)
		if not cookie:
			logger.warning("No %s cookie found after browser fetch", CF_COOKIE_NAME)
			return

		COOKIE_FILE.write_text(json.dumps({CF_COOKIE_NAME: cookie["value"]}, indent=2))
		logger.debug("Saved %s to %s", CF_COOKIE_NAME, COOKIE_FILE)
