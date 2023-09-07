# pylint: skip-file
from unittest.mock import MagicMock, patch
import pandas as pd
from conftest import mock_dataframe, mock_loading_df
from load import (get_db_connection, check_for_duplicate_articles, check_for_duplicate_authors,
                add_to_article_table, add_to_article_author_table, add_to_author_table, add_to_article_version_table,
                retrieve_article_id, retrieve_author_id, load_data)


@patch("load.load_dotenv")
def test_get_connection_raises_error(mock_env):
    """Tests that get_db_connection catches an error with invalid env vars"""
    mock_env.return_value = {}
    result = get_db_connection()
    assert result == None


def test_duplicate_article_returns_none():
    """Tests that check_duplicate_article returns None if it is a duplicate"""
    conn = MagicMock()
    fake_fetch = conn.cursor().__enter__().fetchall
    fake_fetch.return_value = [1, 1]
    result = check_for_duplicate_articles(conn, "test.com")
    assert fake_fetch.call_count == 1
    assert result == None


def test_duplicate_article_returns_url():
    """Tests that url is returned if not a duplicate article"""
    conn = MagicMock()
    fake_fetch = conn.cursor().__enter__().fetchall
    fake_fetch.return_value = []
    result = check_for_duplicate_articles(conn, "test.com")
    assert fake_fetch.call_count == 1
    assert result == "test.com"


def test_duplicate_author_returns_none():
    """Tests that check_duplicate_author returns None if it is a duplicate"""
    conn = MagicMock()
    fake_fetch = conn.cursor().__enter__().fetchall
    fake_fetch.return_value = [1, 1]
    result = check_for_duplicate_articles(conn, "Bob Vance")
    assert fake_fetch.call_count == 1
    assert result == None


def test_duplicate_author_returns_author():
    """Tests that url is returned if not a duplicate article"""
    conn = MagicMock()
    fake_fetch = conn.cursor().__enter__().fetchall
    fake_fetch.return_value = []
    result = check_for_duplicate_authors(conn, "Bob Vance")
    assert fake_fetch.call_count == 1
    assert result == "Bob Vance"


@patch("load.execute_values")
def test_add_article_table_executes(mock_execute, mock_dataframe):
    """Tests that execute_values is called within a mock connection"""
    conn = MagicMock()

    add_to_article_table(conn, mock_dataframe)
    assert mock_execute.call_count == 1
    assert conn.commit.call_count == 1


@patch("load.execute_values")
def test_add_article_author_table_executes(mock_execute, mock_dataframe):
    """Tests that execute_values is called with a mock connection inside add_article_author function"""
    conn = MagicMock()

    add_to_article_author_table(conn, mock_dataframe)
    assert mock_execute.call_count == 1
    assert conn.commit.call_count == 1


@patch("load.execute_values")
def test_add_author_table_executes(mock_execute, mock_dataframe):
    """Tests that execute_values is called with a mock connection inside add_author function"""
    conn = MagicMock()

    add_to_author_table(conn, mock_dataframe)
    assert mock_execute.call_count == 1
    assert conn.commit.call_count == 1


@patch("load.execute_values")
def test_add_article_version_table_executes(mock_execute, mock_dataframe):
    """Tests that execute_values is called with a mock connection inside add_article_version function"""
    conn = MagicMock()

    add_to_article_version_table(conn, mock_dataframe)
    assert mock_execute.call_count == 1
    assert conn.commit.call_count == 1
    

def test_retrieve_author_id():
    """Tests that retrieve author ids returns an id"""
    conn = MagicMock()
    fake_fetch = conn.cursor().__enter__().fetchall
    fake_fetch.return_value = [(1,)]
    result = retrieve_author_id(conn, "Sylvia Plath")
    assert result == 1
    assert fake_fetch.call_count == 1


def test_retrieve_author_id_no_match():
    """Tests that retrieve author ids returns None when no id found"""
    conn = MagicMock()
    fake_fetch = conn.cursor().__enter__().fetchall
    fake_fetch.return_value = []
    result = retrieve_author_id(conn, "Sylvia Plath")
    assert result == None
    assert fake_fetch.call_count == 1


def test_retrieve_article_id():
    """Tests that retrieve article ids returns an id"""
    conn = MagicMock()
    fake_fetch = conn.cursor().__enter__().fetchall
    fake_fetch.return_value = [("test.com",)]
    result = retrieve_article_id(conn, "test.com")
    assert result == "test.com"
    assert fake_fetch.call_count == 1


def test_retrieve_article_id_no_match():
    """Tests that retrieve article ids returns None when no id found"""
    conn = MagicMock()
    fake_fetch = conn.cursor().__enter__().fetchall
    fake_fetch.return_value = []
    result = retrieve_article_id(conn, "test.com")
    assert result == None
    assert fake_fetch.call_count == 1


@patch("load.execute_values")
@patch("load.pd.read_csv")
@patch("load.get_db_connection")
def test_load_data_conn_close_called(mock_connection, mock_read_csv, mock_execute, mock_loading_df):
    """Tests that conn.close is called in function"""
    mock_conn = MagicMock()
    mock_read_csv.return_value = mock_loading_df
    mock_connection.return_value = mock_conn

    load_data()
    assert mock_conn.close.call_count == 1


@patch("load.execute_values")
@patch("load.pd.read_csv")
@patch("load.get_db_connection")
def test_load_data_conn_commit_called(mock_connection, mock_read_csv, mock_execute, mock_loading_df):
    """Tests that conn.close is called in function"""
    mock_conn = MagicMock()
    mock_read_csv.return_value = mock_loading_df
    mock_connection.return_value = mock_conn

    load_data()
    assert mock_conn.commit.call_count == 4