-- Schema file to create tables within DB

DROP DATABASE IF EXISTS news_info;
CREATE DATABASE news_info;
\c news_info; 

CREATE TABLE IF NOT EXISTS article (
    article_id INT GENERATED ALWAYS AS IDENTITY,
    article_url TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    author TEXT NOT NULL,
    PRIMARY KEY (article_id),
    CONSTRAINT check_created_at CHECK (created_at <= NOW()),
    CONSTRAINT check_article_url CHECK (article_url LIKE '%www.%' or article_url LIKE '%WWW.%')
);

insert into article
(article_url, source, created_at, author)
values 
('www.google.com', 'BBC', '2023-01-03 10:10:10', 'Simeon');

CREATE TABLE IF NOT EXISTS scraping_info (
    scraping_info_id INT GENERATED ALWAYS AS IDENTITY,
    scraped_at TIMESTAMP NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    article_id INT NOT NULL,
    PRIMARY KEY(scraping_info_id), 
    FOREIGN KEY (article_id) REFERENCES article(article_id),
    CONSTRAINT check_scraped_at CHECK (scraped_at <= NOW())
);

