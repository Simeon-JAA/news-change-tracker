# pylint: skip-file
"""
Tests transform.py functionality
"""
from datetime import datetime
import pytz
import pandas as pd
from transform import format_time_to_timestamp, format_rss_feed_df
from conftest import mock_dataframe

def test_format_timestamp():
    """tests the format timestamp function correctly formats time"""
    result = format_time_to_timestamp("Mon, 04 Sep 2023 12:02:28 GMT")
    gmt = pytz.timezone("Europe/London")
    assert result == gmt.localize(datetime(2023, 9, 4, 12, 2, 28))

def test_format_rss_feed(mock_dataframe):
    result = format_rss_feed_df(mock_dataframe)
    assert isinstance(result, pd.DataFrame )
    