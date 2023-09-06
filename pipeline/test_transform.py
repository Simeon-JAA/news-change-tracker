# pylint: skip-file
"""
Tests transform.py functionality
"""
from datetime import datetime
import pytz
import pandas as pd
from transform import format_time_to_timestamp, format_rss_feed_df, format_authors, format_scraped_articles_df
from conftest import mock_dataframe, mock_scraped_df

def test_format_timestamp():
    """tests the format timestamp function correctly formats time"""
    result = format_time_to_timestamp("Mon, 04 Sep 2023 12:02:28 GMT")
    gmt = pytz.timezone("Europe/London")
    assert result == gmt.localize(datetime(2023, 9, 4, 12, 2, 28))


def test_format_rss_feed(mock_dataframe):
    """Tests format_rss function returns dataframe"""
    result = format_rss_feed_df(mock_dataframe)
    assert isinstance(result, pd.DataFrame )
    assert "id" in result.columns
    assert "title" in result.columns
    assert "published" in result.columns


def test_format_authors_return_none():
    """tests that function returns none if author is NaN"""
    result = format_authors("NaN")
    assert result is None


def test_format_authors_removes_extras():
    """Tests that function removes '&', 'by ', 'and', etc"""
    result = format_authors("by Scooby & shaggy and Scrappy")
    assert result == ["Scooby", "Shaggy", "Scrappy"]


def test_format_authors_only_names():
    """Tests that author list is returned when columns does not start 'By ' """
    result = format_authors("Velma and Daphne & Fred")
    assert result == ["Velma", "Daphne", "Fred"]


def test_format_scraped_articles_strips_URL(mock_scraped_df):
    """Tests the format_scraped_articles function strips url"""
    result = format_scraped_articles_df(mock_scraped_df)
    assert isinstance(result, pd.DataFrame)
    assert result["url"][0] == "realurl.com"
