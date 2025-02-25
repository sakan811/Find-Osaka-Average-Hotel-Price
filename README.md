# Find the Hotel's Average Room Price in Osaka and Japan

## Table of Contents

- Overview
  - [Osaka Project](#find-the-hotels-average-room-price-in-osaka)
  - [Japan Project](#find-the-hotels-average-room-price-in-japan)
- [Project Status](#status)
- [Visualizations](#visualizations)
  - [Osaka Visualizations](#average-room-price-in-osaka)
  - [Japan Visualizations](#average-room-price-for-all-prefectures-in-japan)
- [Project Details](#project-details)
  - [Osaka Project Details](#find-the-hotels-average-room-price-in-osaka-project)
  - [Japan Project Details](#find-the-hotels-average-room-price-in-japan-project)
- [Data Archive](#collected-data-archive)
- [Usage Guide](#general-guidelines-for-using-the-scraper)
- [Getting Started](#how-to-scrape-hotel-data)
  - [Project Setup](#setup-project)
  - [Database Setup](#setup-a-database)
  - [Authentication Setup](#find-the-necessary-headers)
  - [Using Whole-Month Scraper](#to-scrape-using-whole-month-graphql-scraper)
  - [Using Basic Scraper](#to-scrape-using-basic-graphql-scraper)
  - [Using Japan Scraper](#to-scrape-using-japan-graphql-scraper)
- [Scraper Arguments](#scrapers-arguments)
- [Missing Date Checker](#find-the-missing-dates-in-the-database-using-missing-date-checker)

## Find the Hotel's Average Room Price in Osaka

Showcase **visualizations** about the hotel's **Average Room Price** in **Osaka**.

 **Average Nightly Room Price** for one adult, one room.

Price in **USD**.

## Find the Hotel's Average Room Price in Japan

Showcase **visualizations** about the hotel's **Average Room Price** for all **prefectures** in **Japan**.

 **Average Nightly Room Price** for one adult, one room.

Price in **USD**.

Built on top of [Find the Hotel's Average Room Price in Osaka](#find-the-hotels-average-room-price-in-osaka) project.

## Status

[![CodeQL](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml)

[![Scraper Test](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml)  

[![Scrape](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml)

## Visualizations

### Average Room Price in Osaka

[Click here](docs/VISUALS.md) for visualizations of this project.

### Average Room Price for all Prefectures in Japan

[Click here](docs/VISUALS.md) for visualizations of this project.

## Project Details

### Find the Hotel's Average Room Price in Osaka Project

- Collect **Osaka hotel** property data from Booking.com

- Data **collecting period** for Year 2025: 4 Sep 2024—Present

- Consists of room price from 1 Jan 2025—31 Dec 2025

- Data was collected daily using GitHub action.

- Consists of **Basic GraphQL** and **Whole-Month GraphQL** scraper.

- These scrapers can also be used to scrape data from other cities in Japan.

### Find the Hotel's Average Room Price in Japan Project

- Collect **Japan hotel** property data for all **Prefectures** from Booking.com

- Data collecting dates for Year 2025: 17 Jan 2025.

- Consists of room price from 17 Jan 2025—31 Dec 2025.

- Use **Japan GraphQL** scraper to scrape data.

## Collected Data Archive

[Click here](docs/DATA.md) to access the collected hotel data archive.

## General Guidelines for Using the Scraper

- To scrape only hotel properties, use `--scrape_only_hotel` argument.
- Ensure that Docker Desktop and Postgres container are running.
- Data is appended to the database for both projects.

## How to Scrape Hotel Data

### Setup Project

- Clone this repo: <https://github.com/sakan811/Find-Osaka-Average-Hotel-Price.git>
- Install [Git LFS](https://git-lfs.github.com/)
- Create a virtual environment and activate it.
- Install all dependencies listed in [requirements.txt](requirements.txt)
- Run `playwright install`

### Setup a Database

- Download [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Ensure that Docker Desktop is running.
- Run: `export POSTGRES_DATA_PATH='<your_container_volume_path>'` to set the container volume
  to the directory path of your choice.
- Run: `docker compose up -d`

### Environment Variables

By default, values from the `.env` file will override any existing environment variables. To prevent this behavior and keep existing environment variables, use the `--no_override_env` flag when running the scraper.

For example:

```bash
# Keep existing environment variables (don't override with .env values)
python main.py --city=Tokyo --no_override_env
```

### Find the Necessary Headers

- Run: `python get_auth_headers.py`
  - It will write the headers to an `.env` file.

### To scrape using Whole-Month GraphQL Scraper

- Example usage, with only required arguments for Whole-Month GraphQL Scraper:

  ```bash
  python main.py --whole_mth --year=2024 --month=12 --city=Osaka
  ```

- Scrape data start from the given day of the month to the end of the same month.
  - Default **start day** is 1.
  - **Start day** can be set with `--start_day` argument.

### To scrape using Basic GraphQL Scraper

- Example usage, with only required arguments for Basic GraphQL Scraper:

  ```bash
  python main.py --city=Osaka --check_in=2024-12-25 --check_out=2024-12-26 --scraper              
  ```

### To scrape using Japan GraphQL Scraper

- Example usage, with only required arguments for Japan GraphQL Scraper:

  ```bash
  python main.py --japan_hotel
  ```

- Prefecture to scrape can be specified with `--prefecture` argument, for example:

  - ```bash
    python main.py --japan_hotel --prefecture Tokyo
    ```

  - If `--prefecture` argument is not specified, all prefectures will be scraped.
  - Multiple prefectures can be specified.

    - ```bash
      python main.py --japan_hotel --prefecture Tokyo Osaka
      ```

  - You can use the prefecture name on Booking.com as a reference.

> If the not match error happened (SystemExit exception), please try running the scraper again.

## Scraper's Arguments

[Click here](docs/SCRAPER_ARGS.md) for Scraper's arguments details.

## Find the missing dates in the database using Missing Date Checker

To ensure that all dates of the month were scraped, a function in
[check_missing_dates.py](check_missing_dates.py) will check in the database to find the missing dates.

> _**Made only for the [Find the Hotel's Average Room Price in Osaka](#find-the-hotels-average-room-price-in-osaka) project
  which saves scraped data in HotelPrice table.**_

- To check in the database, use the following command line as an example, only include required argument:

  ```bash
  python check_missing_dates.py --city=Osaka
  ```

- If there are missing dates, a Basic Scraper will automatically start to scrape those dates.
  - **Missing Date Checker** shares arguments with **Basic Scraper**.
  - Arguments parsed to **Missing Date Checker** should be the same as used with **Basic Scraper**.
- Only check the missing dates of the data that was scraped today in **UTC** time.
- Only check the months that were scraped and loaded to the database.
- Year of dates can be specified with `--year`
  - Default is the current year.

> If the not match error happened (SystemExit exception), please try running the Missing Date Checker again.
