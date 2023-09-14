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

   ```
   pip3 install -r requirements.txt
   ```

2. (OPTIONAL) If running on AWS: Provision AWS resources using the Terraform file provided.

   1. Update `.env` file to use your AWS details and RDS url.

   2. Enter relevant values for the variables in `variables.tf` in a `terraform.tfvars` file (should match `.env`).
   3. Run the following commands in the `terraform` directory to set up the AWS cloud resources and enter `yes`:
      ```
      terraform init
      ```
      ```
      terraform apply
      ```
   4. To remove all cloud resources run and enter `yes`:
      ```
      terraform destroy
      ```

3. Create a .env file with the following variables:

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

4. Set up the database using the schema file, run:

   ```
   psql --host [DB_HOST] -f schema.sql
   ```

## Running the pipelines

1. Create docker images for the scraping pipeline and for the comparison pipeline.
   Navigate to each pipeline sub-folder and run the following command, using a relevant image name e.g. 'scraping_pipeline':

   ```
   docker build -t [IMAGE_NAME] .
   ```

   If running on AWS cloud resources (ECS), add `--platform linux/amd64` to the end of the command.

2. The image can be run locally with the following command:

   ```
   docker run -it --env-file ../.env [IMAGE_NAME]
   ```

3. The scraping docker container will extract article information from the BBC RSS feed and upload it to the database provided by the environment variables

   The comparison docker container will extract the latest article information for all articles stored in the database, run comparison analysis, and upload the results into the database, provided there are changes in article information.

4. Locally, these images can be run on a schedule using cron jobs to automatically extract and compare data.

   Alternatively if running on AWS, the docker images can be uploaded to the ECR created by Terraform, and EventBridge schedules can be set up to run the ECS task definitions, using cron in AWS.

## Viewing the dashboard
