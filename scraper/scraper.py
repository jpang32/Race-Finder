# scraper/scraper.py

import json
import logging
import re
import time
from pathlib import Path

import undetected_chromedriver as uc
from curl_cffi import requests as cffi_requests

COOKIE_DIR = Path.home() / ".race-finder"
COOKIE_FILE = COOKIE_DIR / "cookies.json"

_CF_WAIT_INITIAL = 6
_CF_POLL_INTERVAL = 3
_CF_MAX_POLLS = 12

logger = logging.getLogger(__name__)

class RaceScraper:

    def __init__(self):
        COOKIE_DIR.mkdir(parents=True, exist_ok=True)

    def _fetch_page(self, url: str) -> str:
        """Fetch a page, automatically handling Cloudflare protection.

        Tries curl_cffi first (fast), falls back to a real browser if needed.
        Cookies are persisted across calls and across process runs.
        """
        cookies = self._load_cookies()

        # Tier 2: real browser with challenge solving
        logger.info("Falling back to Tier 2 (browser) for %s", url)
        print("curl_cffi blocked — launching browser to solve Cloudflare challenge...")
        html = self._fetch_with_browser(url, cookies)
        return html

    def _read_and_validate_token(self) -> bool:
        """Read the token from the local file and validate it."""
        try:
            with open(COOKIE_FILE, 'r') as file:
                token = file.read().strip()
            # Validate the token (example validation: check if it's not empty)
            if token:
                return True
        except Exception as e:
            logger.error(f"Error reading or validating token: {e}")
        return False

    def _load_cookies(self) -> dict[str, str]:
        """Load saved cookies from disk."""
        if COOKIE_FILE.exists():
            try:
                data = json.loads(COOKIE_FILE.read_text())
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError, OSError:
                pass
        return {}

    def _fetch_with_browser(self, url: str, cookies: dict[str, str]) -> str:
        """Use undetected-chromedriver to solve Cloudflare JS challenges.

        Runs in visible (non-headless) mode because Cloudflare reliably detects
        headless Chrome. After passing the challenge, cookies are saved so future
        requests can use them without needing to open the browser again.
        """
        driver = uc.Chrome(version_main=152)

        try:
            # Inject any saved cookies (must visit the domain first to set them)
            match = re.match(r'^(https?://[^/]+)', url)

            if cookies:
                driver.get(match.group(1))
                time.sleep(1)
                for name, value in cookies.items():
                    driver.add_cookie({"name": name, "value": value})

            driver.get(url)

            # Wait for Cloudflare Turnstile / JS challenge to resolve
            time.sleep(_CF_WAIT_INITIAL)
            html = driver.page_source

            polls = 0
            while self._is_cloudflare_challenge(html) and polls < _CF_MAX_POLLS:
                polls += 1
                logger.info("Waiting for Cloudflare challenge... attempt %d/%d", polls, _CF_MAX_POLLS)
                print(f"Waiting for Cloudflare challenge... attempt {polls}/{_CF_MAX_POLLS}")
                time.sleep(_CF_POLL_INTERVAL)
                html = driver.page_source

            if self._is_cloudflare_challenge(html):
                logger.warning("Cloudflare challenge did not resolve after %d attempts", _CF_MAX_POLLS)
                print("WARNING: Cloudflare challenge did not resolve. You may need to solve it manually.")
                # Give a final window for manual solving
                time.sleep(15)
                html = driver.page_source

            self._save_cookies(driver)

            return html
        finally:
            driver.quit()

    def _save_cookies(self, client: cffi_requests.Session | uc.Chrome, cookies: dict[str, str] | {}):
        """Persist cookies to disk for reuse across runs."""
        if type(client) is cffi_requests.Session:
            if cookies:
                client.cookies.update(cookies)
            new_cookies = client.cookies
        else:
            new_cookies = {c["name"]: c["value"] for c in client.get_cookies()}

        merged = {**cookies, **dict(new_cookies)}

        COOKIE_FILE.write_text(json.dumps(merged, indent=2))
        logger.debug("Saved %d cookies to %s", len(cookies), COOKIE_FILE)

    def parse_page(
        self,
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

        html_content = self._fetch_page(url)

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
