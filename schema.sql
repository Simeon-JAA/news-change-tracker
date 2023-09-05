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

CREATE TABLE IF NOT EXISTS scraping_info (
    scraping_info_id INT GENERATED ALWAYS AS IDENTITY,
    scraped_at TIMESTAMPTZ NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    article_id INT NOT NULL,
    PRIMARY KEY(scraping_info_id),
    FOREIGN KEY (article_id) REFERENCES article(article_id),
    CONSTRAINT check_scraped_at CHECK (scraped_at <= NOW())
);

