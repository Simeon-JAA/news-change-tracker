# news-change-tracker

## Intro

This project aims to track the frequency and scale of changes that happen to news articles online

The project creates an ETL pipeline that parses news article data from different sources' RSS feeds, scrapes additional content
from each article, then uploads it into a RDS database every 30 minutes.

Freshly scraped data can be compared to existing data in the database, and amount of changes, type of changes, and frequency of changes
can be displayed using a Streamlit dashboard.

Terraform has also been used to provision all the necessary AWS resources to run the pipeline and Streamlit apps.

## Set Up

1. Install required packages by running the following command inside the pipeline folder:

   `pip3 install -r requirements.txt`

2. Create a .env file with the following variables:

   ```
   ACCESS_KEY_ID (for AWS)
   SECRET_ACCESS_KEY (for AWS)
   DB_HOST
   DB_USER
   DB_PORT
   DB_PASSWORD
   DB_NAME
   ```

These values will depend on your database set up.

3. Set up the database using the schema file, run:

   `psql --host [DB_HOST] -f schema.sql`

## Running the pipeline

## Viewing the dashboard
