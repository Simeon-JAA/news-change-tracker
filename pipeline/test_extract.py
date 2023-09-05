# pylint: skip-file
"""
TESTS: 
7: test requests status codes
8: test scrape all articles appends list with valid article
9: test scrape skips a url if no valid article


Break down test article into smaller func?
"""
import pytest
import requests.exceptions
import pandas as pd
from unittest.mock import MagicMock, patch
from conftest import rss_feed, bbc_html, bbc_sport_html, bbc_article_dict, bbc_sport_dict
from extract import read_feed, scrape_article, scrape_all_articles


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
    def test_scrape_article_returns_dict(self, mock_request, bbc_html, bbc_article_dict):
        """Tests function returns a dict"""
        mock_response = MagicMock()
        mock_response.content = bbc_html
        mock_request.return_value = mock_response

        result = scrape_article("fakeurl.com")
        assert mock_request.call_count == 1
        assert isinstance(result, dict)
        assert result == bbc_article_dict


    @patch("extract.requests.get")
    def test_scrape_bbc_sport(self, mock_request, bbc_sport_html, bbc_sport_dict):
        """Tests returns a dict for bbc sport article html"""
        mock_response = MagicMock()
        mock_response.content = bbc_sport_html
        mock_request.return_value = mock_response

        result = scrape_article("fakeurl.com")
        assert mock_request.call_count == 1
        assert isinstance(result, dict)
        assert result == bbc_sport_dict
    

    def test_scrape_invalid_url(self):
        """Tests invalid url raises an exception"""
        with pytest.raises(requests.exceptions.ConnectionError):
            scrape_article("https://www.not-a-url.commm")


class TestScrapeAllArticles:
    """Tests for the scrape_all_articles function"""

    @patch("extract.scrape_article")
    def test_returns_dataframe(self, mock_scrape):
        mock_scrape.return_value = {"body": "body",
                                    "headline": "headline"}
        urls = ["url1", "url2", "url3"]
        result = scrape_all_articles(urls)
        assert isinstance(result, pd.DataFrame)
        assert result.shape[0] == 3
    
    def test_invalid_urls_not_added(self):
        urls = ["url", ["url2"]]
        result = scrape_all_articles(urls)
        assert result.shape[0]==0

