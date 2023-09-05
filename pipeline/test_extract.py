# pylint: skip-file
"""
TESTS: 
1:test RSS feed valid URL 
2: and invalid URL
3: test scrape article returns dict
4: test scrape article valid bbc html
5. test valid sport html
6: test invalid html
7: test requests status codes
8: test scrape all articles appends list with valid article
9: test scrape skips a url if no valid article


Break down test article into smaller func?
"""
import pytest
from unittest.mock import MagicMock, patch
from extract import read_feed, scrape_article

@pytest.fixture
def rss_feed():
    return {
        "entries" : [
            {
            "title" : "article title",
            "summary" : "article summary"
            }
        ]
    }

class TestReadFeed:
    """Tests the read_feed function"""

    @patch("extract.feedparser.parse")
    def test_valid_url(self, mock_parse, rss_feed):
        """Tests that read_feed returns a dict with a valid URL"""
        mock_parse.return_value = rss_feed
        result = read_feed("https:/www.url.com")
        assert result == rss_feed
        assert isinstance(result, dict)
    
    
    @patch("extract.feedparser.parse")
    def test_invalid_url(self, mock_parse):
        """Tests invalid url returns empty dict with empty entries list"""
        mock_parse.return_value = {"entries" : []}
        result = read_feed("not a url")
        assert isinstance(result, dict)
        assert result["entries"] == []


class TestScrapeArticle:
    """Tests for scrape_article function"""

    @patch("extract.requests.get")
    def test_scrape_article_returns_dict(self, mock_request):
        """Tests function returns a dict"""
        mock_request.return_value = 
