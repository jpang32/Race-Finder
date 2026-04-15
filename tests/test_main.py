from unittest.mock import MagicMock, patch

import pytest

from src.main import _get_crawl_delay


@pytest.mark.parametrize(
    "text, expected_crawl_delay",
    [
        ("Crawl-Delay: 16", 16),
        ("crawl-delay:::   6786134jhgjhdsg", 6786134),
    ]
)
@patch("main.requests")
def test_get_crawl_delay(mocked_request, text, expected_crawl_delay):
    mock_get = MagicMock()
    mock_get.text = text
    mocked_request.get.return_value = mock_get

    output = _get_crawl_delay("dummy_base_url")
    assert output == expected_crawl_delay