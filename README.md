# Find the Hotel's Average Room Price in Osaka

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
### Average Room Price in Osaka: 
[Click here](docs/VISUALS.md) for visualizations of this project.

### Average Room Price for all Prefectures in Japan: 

* [Power BI](https://app.powerbi.com/view?r=eyJrIjoiZjIwNWExZTktZTFmYi00YmY2LWE1NmQtYWQ5NWFhMjhmNzM0IiwidCI6ImZlMzViMTA3LTdjMmYtNGNjMy1hZDYzLTA2NTY0MzcyMDg3OCIsImMiOjEwfQ%3D%3D)  

* [Instagram](https://www.instagram.com/p/C_nnLTmuB8b/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==)  

* [Facebook](https://www.facebook.com/share/p/vAER9MMiZm6anSd2/)


## Project Details
### Find the Hotel's Average Room Price in Osaka Project
- Collect **Osaka hotel** property data from Booking.com

- Data **collecting period** for Year 2025: 4 Sep 2024—Present

- Consists of room price from 4 Sep 2024—Present

- Data was collected daily using GitHub action.

- Consists of **Basic GraphQL** and **Whole-Month GraphQL** scraper.

- These scrapers can also be used to scrape data from other cities in Japan.

### Find the Hotel's Average Room Price in Japan Project

- Collect **Japan hotel** property data for all **Prefectures** from Booking.com

- Data collecting dates: 23 Aug 2024.

- Use **Japan GraphQL** scraper to scrape data.

## Collected Data Archive
[Click here](https://huggingface.co/datasets/sakanbeer88/osaka-and-japan-avg-hotel-room-price-data) to access the collected hotel data hosted on HuggingFace

## How to Scrape Hotel Data
### Setup Project
- Clone this repo: https://github.com/sakan811/Find-Osaka-Average-Hotel-Price.git
- Create a virtual environment and activate it.
- Install all dependencies listed in [requirements.txt](requirements.txt)
- Rename a `.env.example` to `.env`
  
### Find your **User Agent**:
  - Go to https://www.whatismybrowser.com/detect/what-is-my-user-agent/
  - Enter your User Agent into your **.env** file:
    - User-Agent ➡ USER_AGENT

### Find Necessary Headers

1. **Open Booking.com**
   - Go to [Booking.com](https://www.booking.com).
   - Search for any destination (like "Tokyo" or "New York") to see a list of available places.

2. **Open Developer Tools:**
   - Make sure you are on the page showing the available places for booking.
   - Scroll down a bit on the page.
   - Open the Developer Tools (a set of tools to inspect web pages):
     - **For Chrome:**
       - Right-click anywhere on the page.
       - Click on `Inspect`.
       - Click on the `Network` tab at the top of the Developer Tools.
     - **For Firefox:**
       - Right-click anywhere on the page.
       - Click on `Inspect`.
       - Click on the `Network` tab at the top.

3. **Find GraphQL Request:**
   - In the **filter** bar at the top of the Network tab, type `graphql`.
     
   > If you don't see any requests start with `graphql` or named `graphql` right away, scroll down the Booking.com page a little more. 
   > This will load more requests in the Network tab, and you may find the `graphql` request there.

4. **Inspect a Request:**
   - Click on the request start with `graphql` or named `graphql` from the list in the Network tab.
   - Look for the section labeled **Headers**. This section contains details about what was sent to the server.

5. **Find the Necessary Headers:**
   - Look for these specific headers in the Headers section:
     - `X-BOOKING-CONTEXT-ACTION-NAME`
     - `X-BOOKING-CONTEXT-AID`
     - `X-BOOKING-CSRF-TOKEN`
     - `X-BOOKING-ET-SERIALIZED-STATE`
     - `X-BOOKING-PAGEVIEW-ID`
     - `X-BOOKING-SITE-TYPE-ID`
     - `X-BOOKING-TOPIC`

6. **Copy Header Values:**
   - For each header, right-click on it and select `Copy Value`. This copies the information to your clipboard.

7. **Save the Values Locally:**
   - Open a text editor and create a new file named `.env`.
   - Paste each copied value into the file next to its corresponding name, like this:
     ```
     X_BOOKING_CONTEXT_ACTION_NAME=copied_action_name
     X_BOOKING_CONTEXT_AID=copied_aid
     X_BOOKING_CSRF_TOKEN=copied_csrf_token
     X_BOOKING_ET_SERIALIZED_STATE=copied_serialized_state
     X_BOOKING_PAGEVIEW_ID=copied_pageview_id
     X_BOOKING_SITE_TYPE_ID=copied_site_type_id
     X_BOOKING_TOPIC=copied_topic
     ```


### General Guidelines for Using the Scraper
- To scrape only hotel properties, use `--scrape_only_hotel` argument.
- The SQLite database is created automatically if it doesn't exist.
- The DuckDB database is created automatically if it doesn't exist.
    
### To scrape using Whole-Month GraphQL Scraper:
- Example usage, with only required arguments for Whole-Month GraphQL Scraper:
  ```bash
  python main.py --whole_mth --year=2024 --month=12 --city=Osaka  \
                 --sqlite_name=avg_japan_hotel_price_test.db
  ```
- Scrape data start from the given day of the month to the end of the same month.
  - Default **start day** is 1.
  - **Start day** can be set with `--start_day` argument.
- Data is saved to **SQLite**.

### To scrape using Basic GraphQL Scraper:
- Example usage, with only required arguments for Basic GraphQL Scraper:
  ```bash
  python main.py --city=Osaka --check_in=2024-12-25 --check_out=2024-12-26 --scraper \
                 --sqlite_name=avg_japan_hotel_price_test.db
  ```
- Data is saved to **SQLite**.

### To scrape using Japan GraphQL Scraper:
- Example usage, with only required arguments for Japan GraphQL Scraper:
  ```bash
  python main.py --japan_hotel --duckdb_name=japan_hotel_data_test.duckdb
  ```
- Data is saved to **DuckDB**.

> If the not match error happened (SystemExit exception), please try running the scraper again.

## Scraper's Arguments
[Click here](docs/SCRAPER_ARGS.md) for Scraper's arguments details.


## Find the missing dates in the database using Missing Date Checker
To ensure that all dates of the month were scraped, a function in
[check_missing_dates.py](check_missing_dates.py) will check in the given SQLite database to find the missing dates.

> _**Made only for the [Find the Hotel's Average Room Price in Osaka](#find-the-hotels-average-room-price-in-osaka) project
  which saves scraped data in SQLite.**_

- To check in the database, use the following command line as an example, only include required argument:
  ```bash
  python check_missing_dates.py --city=Osaka
  ```
- If there are missing dates, a Basic Scraper will automatically start to scrape those dates.
  - **Missing Date Checker** shares arguments with **Basic Scraper**.
  - Arguments parsed to **Missing Date Checker** should be the same as used with **Basic Scraper**.
- Only check the missing dates of the data that was scraped today in **UTC** time.
- Only check the months that were scraped and loaded to the database.
- The SQLite database can be specified with `--sqlite_name` 
  - Default is `avg_japan_hotel_price_test.db`
- Year of dates can be specified with `--year`
  - Default is the current year.

> If the not match error happened (SystemExit exception), please try running the Missing Date Checker again.
