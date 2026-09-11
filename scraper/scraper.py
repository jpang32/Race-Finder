"""Two-tier scraping strategy for bypassing Cloudflare protection.

Tier 1: curl_cffi with browser TLS fingerprint impersonation (fast, no browser needed).
Tier 2: undetected-chromedriver with Turnstile wait (slower, but handles JS challenges).

Cookies are persisted to disk so subsequent runs can skip challenges entirely.
"""

import json
import logging
import ssl
import time
from pathlib import Path

import undetected_chromedriver as uc
from curl_cffi import requests as cffi_requests

# undetected-chromedriver uses urllib internally to download the ChromeDriver
# binary. On macOS, Python's bundled OpenSSL often can't find the system
# certificate chain, causing CERTIFICATE_VERIFY_FAILED. This tells urllib
# to skip verification for that download only.
ssl._create_default_https_context = ssl._create_unverified_context

logger = logging.getLogger(__name__)

COOKIE_DIR = Path.home() / ".race-finder"
COOKIE_FILE = COOKIE_DIR / "cookies.json"

# How long to wait for Cloudflare Turnstile to resolve in the browser fallback
_CF_WAIT_INITIAL = 6
_CF_POLL_INTERVAL = 3
_CF_MAX_POLLS = 12


def _ensure_cookie_dir():
	COOKIE_DIR.mkdir(parents=True, exist_ok=True)


def _load_cookies() -> dict[str, str]:
	"""Load saved cookies from disk."""
	if COOKIE_FILE.exists():
		try:
			data = json.loads(COOKIE_FILE.read_text())
			if isinstance(data, dict):
				return data
		except json.JSONDecodeError, OSError:
			pass
	return {}


def _save_cookies(cookies: dict[str, str]):
	"""Persist cookies to disk for reuse across runs."""
	_ensure_cookie_dir()
	COOKIE_FILE.write_text(json.dumps(cookies, indent=2))
	logger.debug("Saved %d cookies to %s", len(cookies), COOKIE_FILE)


def _is_cloudflare_challenge(html: str) -> bool:
	"""Detect whether the response is a Cloudflare challenge page."""
	markers = ["Just a moment...", "Checking your browser", "cf-challenge", "challenge-platform"]
	return any(m in html for m in markers)


def _fetch_with_curl_cffi(url: str, cookies: dict[str, str]) -> str | None:
	"""Tier 1: Use curl_cffi to impersonate a real browser's TLS fingerprint.

	This is fast and avoids spinning up a full browser. It works when Cloudflare
	only checks the TLS handshake / JA3 fingerprint and doesn't require a JS challenge.
	"""
	session = cffi_requests.Session(impersonate="chrome")

	if cookies:
		session.cookies.update(cookies)

	try:
		resp = session.get(url, timeout=15)
	except Exception:
		logger.warning("curl_cffi request failed for %s", url, exc_info=True)
		return None

	if resp.status_code != 200:
		logger.info("curl_cffi got status %d for %s", resp.status_code, url)
		return None

	html = resp.text

	if _is_cloudflare_challenge(html):
		logger.info("curl_cffi hit Cloudflare challenge for %s — will fall back to browser", url)
		return None

	# Success — update persisted cookies with any new values from this session
	merged = {**cookies, **dict(session.cookies)}
	_save_cookies(merged)

	return html


def _fetch_with_browser(url: str, cookies: dict[str, str]) -> str:
	"""Tier 2: Use undetected-chromedriver to solve Cloudflare JS challenges.

	Runs in visible (non-headless) mode because Cloudflare reliably detects
	headless Chrome. After passing the challenge, cookies are saved so future
	requests can use Tier 1 directly.
	"""
	options = uc.ChromeOptions()
	# Non-headless is intentional — headless gets detected by modern Cloudflare.
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")

	driver = uc.Chrome(options=options, version_main=152)

	try:
		# Inject any saved cookies (must visit the domain first to set them)
		if cookies:
			driver.get(url.split("/classic")[0] or url)
			time.sleep(1)
			for name, value in cookies.items():
				driver.add_cookie({"name": name, "value": value})

		driver.get(url)

		# Wait for Cloudflare Turnstile / JS challenge to resolve
		time.sleep(_CF_WAIT_INITIAL)
		html = driver.page_source

		polls = 0
		while _is_cloudflare_challenge(html) and polls < _CF_MAX_POLLS:
			polls += 1
			logger.info("Waiting for Cloudflare challenge... attempt %d/%d", polls, _CF_MAX_POLLS)
			print(f"Waiting for Cloudflare challenge... attempt {polls}/{_CF_MAX_POLLS}")
			time.sleep(_CF_POLL_INTERVAL)
			html = driver.page_source

		if _is_cloudflare_challenge(html):
			logger.warning("Cloudflare challenge did not resolve after %d attempts", _CF_MAX_POLLS)
			print("WARNING: Cloudflare challenge did not resolve. You may need to solve it manually.")
			# Give a final window for manual solving
			time.sleep(15)
			html = driver.page_source

		# Persist browser cookies so Tier 1 can reuse them next time
		browser_cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
		merged = {**cookies, **browser_cookies}
		_save_cookies(merged)

		return html
	finally:
		driver.quit()


def fetch_page(url: str) -> str:
	"""Fetch a page, automatically handling Cloudflare protection.

	Tries curl_cffi first (fast), falls back to a real browser if needed.
	Cookies are persisted across calls and across process runs.
	"""
	cookies = _load_cookies()

	# Tier 1: curl_cffi with browser impersonation
	html = _fetch_with_curl_cffi(url, cookies)
	if html is not None:
		logger.info("Tier 1 (curl_cffi) succeeded for %s", url)
		return html

	# Tier 2: real browser with challenge solving
	logger.info("Falling back to Tier 2 (browser) for %s", url)
	print("curl_cffi blocked — launching browser to solve Cloudflare challenge...")
	html = _fetch_with_browser(url, cookies)
	return html
