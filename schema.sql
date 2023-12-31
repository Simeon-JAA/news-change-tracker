-- Schema file to create tables within DB

DROP DATABASE IF EXISTS news_info;
CREATE DATABASE news_info;
\c news_info;

CREATE TABLE IF NOT EXISTS article (
    article_id INT GENERATED ALWAYS AS IDENTITY,
    article_url TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (article_id),
    CONSTRAINT check_created_at CHECK (created_at <= NOW()),
    CONSTRAINT check_article_url CHECK (article_url LIKE '%www.%' or article_url LIKE '%WWW.%')
);

CREATE TABLE IF NOT EXISTS author (
    author_id INT GENERATED ALWAYS AS IDENTITY,
    author_name TEXT NOT NULL,
    PRIMARY KEY (author_id)
);

CREATE TABLE IF NOT EXISTS article_author (
    article_author_id INT GENERATED ALWAYS AS IDENTITY,
    article_id INT,
    author_id INT,
    FOREIGN KEY (article_id) REFERENCES article(article_id),
    FOREIGN KEY (author_id) REFERENCES author(author_id)
);

CREATE TABLE IF NOT EXISTS article_version (
    article_version_id INT GENERATED ALWAYS AS IDENTITY,
    scraped_at TIMESTAMPTZ NOT NULL,
    heading TEXT NOT NULL,
    body TEXT NOT NULL,
    article_id INT NOT NULL,
    PRIMARY KEY(article_version_id),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

CREATE SCHEMA changes;

SET SEARCH_PATH TO changes;

CREATE TYPE change_types AS ENUM ('body', 'heading');

CREATE TABLE IF NOT EXISTS article_change (
    article_change_id INT GENERATED ALWAYS AS IDENTITY,
    article_id INT NOT NULL,
    article_url TEXT NOT NULL,
    change_type change_types,
    previous_version TEXT NOT NULL,
    current_version TEXT NOT NULL,
    last_scraped TIMESTAMPTZ NOT NULL,
    current_scraped TIMESTAMPTZ NOT NULL,
    similarity FLOAT NOT NULL,
    PRIMARY KEY (article_change_id)
);
