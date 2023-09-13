# pylint: skip-file
"""
Tests load.py functionality
"""
from unittest.mock import MagicMock, patch
import pandas as pd
from load import add_to_article_change_table, add_to_article_version_table, load_data
from conftest import mock_loading_df, mock_article_changes


@patch("load.execute_values")
@patch("pandas.DataFrame.to_records")
def test_add_to_article_version_executes_sql(mock_to_records, mock_execute, mock_loading_df):
    """Tests that the db connection executes sql"""
    conn = MagicMock()
    result = add_to_article_version_table(conn, mock_loading_df)
    assert mock_execute.call_count == 1
    assert conn.commit.call_count == 1


@patch("load.execute_values")
@patch("pandas.DataFrame.to_records")
def test_add_to_article_change_executes_sql(mock_to_records, mock_execute, mock_loading_df):
    """Tests that the db connection executes sql"""
    conn = MagicMock()
    result = add_to_article_change_table(conn, mock_loading_df)
    assert mock_execute.call_count == 1
    assert conn.commit.call_count == 1



@patch("load.get_db_connection")
@patch("load.load_dotenv")
def test_load_data_closes_connection(mock_envs, mock_conn):
    """Tests that load_data closes db connection"""
    conn = MagicMock()
    mock_conn.return_value = conn
    mock_close = conn.close
    result = load_data()
    assert mock_conn.call_count == 1
    assert mock_close.call_count == 1


@patch("load.add_to_article_version_table")
@patch("load.add_to_article_change_table")
@patch("pandas.read_csv")
@patch("load.get_db_connection")
@patch("load.load_dotenv")
def test_load_data_calls_sub_routines(mock_envs, mock_conn, mock_read, mock_add_change, mock_add_version, mock_article_changes):
    """Tests that the functions are called as part of main routine"""
    mock_read.return_value = mock_article_changes
    conn = MagicMock()
    mock_conn.return_value = conn
    load_data()
    assert mock_add_change.call_count == 1
    assert mock_add_version.call_count == 1


