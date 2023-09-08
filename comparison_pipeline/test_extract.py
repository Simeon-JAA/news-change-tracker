# pylint: skip-file
"""
Tests extract.py functionality
"""

import requests
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from conftest import bbc_article_dict, bbc_html, bbc_sport_dict, bbc_sport_html
from extract import get_db_connection, get_urls_from_article_table, scrape_article, scrape_all_articles, extract_data


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


class TestDBConn:
    """Tests for get_db_connection func"""

    @patch("extract.load_dotenv")
    def test_get_connection_raises_error(self, mock_env):
        """Tests that get_db_connection catches an error with invalid env vars"""
        mock_env.return_value = {}
        result = get_db_connection()
        assert result == None


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


class TestGetURLs:
    """Tests the get_url_from_table function"""

    def test_get_urls_returns_list(self):
        """Tests that the function returns empty list if no data retrieved"""
        mock_conn = MagicMock()
        result = get_urls_from_article_table(mock_conn)
        assert result == []
    
    def test_get_urls_returns_list(self):
        """Tests that a list of urls is returned"""
        mock_conn = MagicMock()
        fake_fetch = mock_conn.cursor().__enter__().fetchall
        fake_fetch.return_value = [["url"], ["url2"], ["url3"]]
        result = get_urls_from_article_table(mock_conn)
        assert result == ["url", "url2", "url3"]


class TestExtract:
    """Tests the extract_data function"""
    
    @patch("extract.scrape_all_articles")
    @patch("extract.get_urls_from_article_table")
    @patch("extract.get_db_connection")
    def test_extract_calls_close(self, mock_conn, mock_urls, mock_scrape):
        """Tests that conn.close() is called"""
        conn = MagicMock()
        mock_conn.return_value = conn
        extract_data()
        assert mock_conn.call_count == 1
        assert mock_urls.call_count ==1
        assert mock_scrape.call_count == 1
        assert conn.close.call_count == 1
