# pylint: skip-file
"""
Tests transform.py functionality
"""
from unittest.mock import MagicMock, patch
import pandas as pd
from transform import (identify_changes, format_comparison, changes_to_article, double_change_to_article, format_article_version_update,
                       retrieve_article_id, transform_data)
from conftest import mock_loading_df, mock_changed_df, mock_compared_df, mock_compared_double_diff_df


class TestIdentifyChanges:
    """Tests for the identify_changes function"""
    
    def test_identify_changes_returns_dataframe(self, mock_changed_df, mock_loading_df):
        """Tests that a dataframe is returned"""

        result = identify_changes(mock_changed_df, mock_loading_df)
       
        assert isinstance(result, pd.DataFrame)
        assert result["heading"]["updated"][0] == "new headline"
        assert all([col in result.columns for col in ["body", "heading"]])


# class TestFormatComparison:
#     """Tests for the format_comparison function"""
#     pass 

class TestFormatArticleVersionUpdate():
    """Tests for the format_article_version_update function"""

    @patch("transform.retrieve_article_id")
    def test_format_article_returns_df(self, mock_retrieve, mock_compared_df):
        """Tests that a dataframe is returned"""
        conn = MagicMock()
        result = format_article_version_update(mock_compared_df, conn)
        assert mock_retrieve.call_count == 1
        assert isinstance(result, pd.DataFrame)
        assert all(col in result.columns for col in ["scraped_at", "heading", "body", "article_id"])
    

class TestChangesToArticle:
    """Tests for the changes_to_article function"""
    
    def test_changes_to_article_body(self, mock_compared_df):
        """Tests function returns dataframe"""
        result = changes_to_article(mock_compared_df, "body", "heading")
        
        assert isinstance(result, pd.DataFrame)
        assert "heading" not in result.columns
        assert all(col in result.columns for col in ["current", "previous", "article_url", \
                    "current_scraped_at", "previous_scraped_at", "type_of_change"])

class TestRetrieveArticleId:
    """Tests for retrieve_id function"""
    
    def test_data_fetched(self):
        conn = MagicMock()
        mock_fetch = conn.cursor().__enter__().fetchone
        mock_fetch.return_value = ("1")
        result = retrieve_article_id(conn, "www.test.com")
        assert mock_fetch.call_count == 1
        assert result == "1"

class TestDoubleChanges:
    """Tests for the double_changes_to_article function"""
    
    def test_changes_to_article_body_and_heading(self, mock_compared_double_diff_df):
        """Tests function returns dataframe"""
        result = double_change_to_article(mock_compared_double_diff_df)
        
        assert isinstance(result, pd.DataFrame)
        assert "body" not in result.columns
        assert "heading" not in result.columns
        assert all(col in result.columns for col in ["current", "previous", "article_url", \
                    "current_scraped_at", "previous_scraped_at", "type_of_change"])
