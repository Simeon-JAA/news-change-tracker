# pylint: skip-file
"""
Tests transform.py functionality
"""
from unittest.mock import MagicMock, patch
import pandas as pd
from transform import (identify_changes, format_comparison, changes_to_article, double_change_to_article, format_article_version_update,
                       retrieve_article_id, transform_data)
from conftest import mock_loading_df, mock_changed_df, mock_compared_df


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
    

class TestChangesToArticle:
    """Tests for the changes_to_article function"""
    
    def test_changes_to_article_body(self, mock_compared_df):
        """Tests function returns dataframe"""
        result = changes_to_article(mock_compared_df, "heading", "body")
        
        assert isinstance(result, pd.DataFrame)


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
    
    def test_changes_to_article_body_and_heading(self, mock_compared_df):
        """Tests function returns dataframe"""
        result = double_change_to_article(mock_compared_df)
        
        assert isinstance(result, pd.DataFrame)