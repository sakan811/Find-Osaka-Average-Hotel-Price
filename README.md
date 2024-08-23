# Find the Hotel's Average Room Price in Osaka 

Showcase **visualizations** about the hotel's **Average Room Price** in **Osaka**.

 **Average Nightly Room Price** for one adult, one room.

Price in **USD**.

## Find the Hotel's Average Room Price in Japan

Showcase **visualizations** about the hotel's **Average Room Price** for all **prefectures** in **Japan**.

 **Average Nightly Room Price** for one adult, one room.

Price in **USD**.

Built on top of [Find the Hotel's Average Room Price in Osaka](#find-the-hotels-average-room-price-in-osaka-) project.

## Status
[![CodeQL](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml)    

[![Scraper Test](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml)  

[![Scrape](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml)

## Visualizations
### Average Room Price in Osaka: 

* [Power BI](https://app.powerbi.com/view?r=eyJrIjoiOGFiNzQ1Y2UtZTVlOS00MzkyLTlmN2EtMDY2YWVlNzFiNTIyIiwidCI6ImZlMzViMTA3LTdjMmYtNGNjMy1hZDYzLTA2NTY0MzcyMDg3OCIsImMiOjEwfQ%3D%3D)  

Data as of 8 Aug 2024:

* [Instagram](https://www.instagram.com/p/C-mqUHJvnsM/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==)  

* [Facebook](https://www.facebook.com/permalink.php?story_fbid=pfbid0o5zpeChkd3cLQByBQ583cP3hDp4aJmY3aB8MpHJRagS13JGhZ9wYLVVU3uiUFVRDl&id=61553626169836)

### Average Room Price for all Prefectures in Japan: 



## Project Details
### Find the Hotel's Average Room Price in Osaka Project
Collect **Osaka hotel** property data from Booking.com

Data **collecting period**: 16 May 2024 to 23 Aug 2024.

Consists of room price from **16 May 2024** to **31 Dec 2024**.

Data was collected daily using GitHub action.

This script can also be used to scrape data from other cities in Japan.

#### Collected Data:
[Osaka Hotel Room Price Record](https://drive.google.com/file/d/1NE0zhRcm1Y8PCpsoY5H5fSsTXu01nF10/view?usp=sharing)
- 8,511,577 rows

[Osaka Average Nightly Room Price by Date](https://drive.google.com/file/d/1oNuFmVIyX3wPSSt4a9i0wpbFYWAyTcYk/view?usp=sharing)
- 230 rows

### Find the Hotel's Average Room Price in Japan Project

Collect **Japan hotel** property data for all **Prefectures** from Booking.com

Data collecting dates: 23 Aug 2024.

Data was collected daily using GitHub action.

## To scrape hotel data
### Setup Project
- Clone this repo: https://github.com/sakan811/Find-Osaka-Average-Hotel-Price.git
- Create a virtual environment and activate it.
- Install all dependencies listed in [requirements.txt](requirements.txt)
- Create a **.env** file in the root of your project directory with the following content:
  ```
  USER_AGENT=
  ```
- Find your **User Agent**:
  - Go to https://www.whatismybrowser.com/detect/what-is-my-user-agent/
  - Enter your User Agent into your **.env** file:
    - User-Agent ➡ USER_AGENT
    
### To scrape using Whole-Month GraphQL Scraper:
- Example usage, with only required arguments for Whole-Month GraphQL Scraper:
  ```bash
  python main.py --whole_mth=True --year=2024 --month=12 --city=Osaka
  ```
- Scrape data start from the given day of the month to the end of the same month.
  - Default **start day** is 1.
  - **Start day** can be set with `--start_day` argument.
- Data is saved to **SQLite**.
  - The SQLite database is created automatically if it doesn't exist.
  - Default SQLite path is `avg_japan_hotel_price_test.db`.
  - SQLite path can be set with `--sqlite_name` argument.

### To scrape using Basic GraphQL Scraper:
- Example usage, with only required arguments for Basic GraphQL Scraper:
  ```bash
  python main.py --city=Osaka --check_in=2024-12-25 --check_out=2024-12-26
  ```
- Data is saved to **SQLite**.
  - The SQLite database is created automatically if it doesn't exist.
  - Default SQLite path is `avg_japan_hotel_price_test.db`.
  - SQLite path can be set with `--sqlite_name` argument.

### To scrape using Japan GraphQL Scraper:
- Example usage, with only required arguments for Japan GraphQL Scraper:
  ```bash
  python main.py --japan_hotel=True
  ```
- Data is saved to **DuckDB**.
  - The DuckDB database is created automatically if it doesn't exist.
  - Default DuckDB path is `japan_hotel_data_test.duckdb`.
  - DuckDB path can be set with `--duckdb_name` argument.

## Scraper's Arguments
### `--scraper`
- **Type**: `bool`
- **Default**: `True`
- **Description**: Determines whether to use the basic GraphQL scraper. By default, this is set to `True`.

### `--whole_mth`
- **Type**: `bool`
- **Default**: `False`
- **Description**: If set to `True`, the Whole-Month GraphQL scraper is used. The default value is `False`.

### `--city`
- **Type**: `str`
- **Description**: Specifies the city where the hotels are located.

### `--country`
- **Type**: `str`
- **Description**: Specifies the country where the hotels are located. Default is Japan.

### `--check_in`
- **Type**: `str`
- **Description**: The check-in date for the hotel stay. The date should be in `YYYY-MM-DD` format.

### `--check_out`
- **Type**: `str`
- **Description**: The check-out date for the hotel stay. The date should be in `YYYY-MM-DD` format.

### `--group_adults`
- **Type**: `int`
- **Default**: `1`
- **Description**: Specifies the number of adults in the group. The default value is `1`.

### `--num_rooms`
- **Type**: `int`
- **Default**: `1`
- **Description**: Specifies the number of rooms required for the group. The default value is `1`.

### `--group_children`
- **Type**: `int`
- **Default**: `0`
- **Description**: Specifies the number of children in the group. The default value is `0`.

### `--selected_currency`
- **Type**: `str`
- **Default**: `'USD'`
- **Description**: The currency for the room prices. By default, this is set to `'USD'`.

### `--scrape_only_hotel`
- **Type**: `bool`
- **Default**: `True`
- **Description**: If set to `True`, the scraper will only target hotel properties. The default value is `True`.

### `--sqlite_name`
- **Type**: `str`
- **Default**: `'avg_japan_hotel_price_test.db'`
- **Description**: The name of the SQLite database file to use. The default value is `'avg_japan_hotel_price_test.db'`.

### `--year`
- **Type**: `int`
- **Description**: Specifies the year to scrape. This argument is required for Whole-Month Scraper.

### `--month`
- **Type**: `int`
- **Description**: Specifies the month to scrape. This argument is required for Whole-Month Scraper.

### `--start_day`
- **Type**: `int`
- **Default**: `1`
- **Description**: Specifies the day of the month to start scraping from. The default value is `1`.

### `--nights`
- **Type**: `int`
- **Default**: `1`
- **Description**: Specifies the length of stay in nights. The default value is `1`.


## Find the missing dates in the database using Missing Date Checker
To ensure that all dates of the month were scraped, a function in
[check_missing_dates.py](check_missing_dates.py) will check in the given SQLite database to find the missing dates.

_**Made only for the [Find the Hotel's Average Room Price in Osaka](#find-the-hotels-average-room-price-in-osaka-) project
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

## Code Base Details 
[Click here](docs/DOCS.md) to read a brief docs of the scripts.


