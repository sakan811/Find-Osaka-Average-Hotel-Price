# Find the Hotel's Average Room Price in Osaka 

Showcase visualizations about the hotel's Average Room Price in Osaka.

## Status
Latest Project Update: 30 July 2024

[![CodeQL](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml)    

[![Scraper Test](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml)  

[![Scrape](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml)

## Visualizations
[Power BI](https://app.powerbi.com/view?r=eyJrIjoiOGFiNzQ1Y2UtZTVlOS00MzkyLTlmN2EtMDY2YWVlNzFiNTIyIiwidCI6ImZlMzViMTA3LTdjMmYtNGNjMy1hZDYzLTA2NTY0MzcyMDg3OCIsImMiOjEwfQ%3D%3D)  

Data as of 22 July 2024:

[Instagram](https://www.instagram.com/p/C9uvDanPaTQ/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==)  

[Facebook](https://www.facebook.com/permalink.php?story_fbid=pfbid07vR488Jh2SZVAZTC51FfYUNVUabxq7Yu3aQzVRVeFqwfQeZUmy5z1NFHTCjV7uc6l&id=61553626169836)

## Project Details
Collect Osaka hotel property data from Booking.com

Data collecting start date: 16 May 2024.

Data was collected daily using GitHub action.

This script can also be used to scrape data from other cities.

## Code Base Details 
### To scrape hotel data
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
- Go to [set_details.py](set_details.py)
  - Set the parameters of the 'Details' dataclass as needed.
    - Example:
    ```
    # Set booking details.
    city: str = 'Osaka'  # city where the hotels are located.
  
    # Check-in and Check-out are used only when using the Basic GraphQL Scraper
    check_in: str = '2024-12-01'
    check_out: str = '2024-12-12'
  
    group_adults: int = 1  # number of adults
    num_rooms: int = 1  # number of rooms
    group_children: int = 0  # number of children
    selected_currency: str = 'USD'  # currency of the room price
    scrape_only_hotel: bool = True  # whether to scrape data that is only hotel properties.

    # Optional
    # Set the start date and number of nights when using Whole-Month GraphQL Scraper
    start_day: int = 1  # day to start scraping
    month: int = 12  # month to start scraping
    year: int = 2024  # year to start scraping
    nights: int = 1  # number of night to scrape. this determines the room price of the hotels.
   
    # Set SQLite database name
    sqlite_name: str = 'avg_japan_hotel_price_test.db'
    ```
- To scrape using Whole-Month GraphQL Scraper:
  - Run the following command via command line terminal:
    ```  
    python main.py --whole_mth=True
    ```
  - Scrape data start from the given start date to the end of the same month.
  - Be **careful** with **start_day** variable in [set_details.py](set_details.py), 
  as the **Whole-Month Scraper** starts from the day specified in **start_day** variable 
  in [set_details.py](set_details.py) 

- To scrape using Basic GraphQL Scraper:
  - Run the following command via command line terminal:
    ```  
    python main.py 
    ```
  - Scrape data based on the given **check-in** and **check-out date** in [set_details.py](set_details.py).
- Data is saved to SQLite.
  - The SQLite database is created automatically if it doesn't exist in the given path set in [set_details.py](set_details.py).

### To find the missing dates in the database
To ensure that all dates of the month were scraped, a function in
[check_missing_dates.py](check_missing_dates.py) will check in the given SQLite database to find the missing dates.
- To check in the database, use the following command line:
  ```  
  python check_missing_dates.py 
  ``` 
  - ```--check_db``` should be follow by the path of the database, without any quote.
- If there are missing dates, a Basic Scraper will automatically start to scrape those dates.
- Only check the missing dates of the data that was scraped today.
- Only check the months that were scraped and loaded to the database.
- Check the database specified in [set_details.py](set_details.py) via the **sqlite_name** variable.

### Dataclass
[set_details.py](set_details.py)
- A **dataclass** designed to encapsulate various **parameters** required for **scraping** hotel data.
  - The **parameters** are booking details, e.g., city, check-in, check-out, etc.
  
### [japan_avg_hotel_price_finder](japan_avg_hotel_price_finder) Package
[configure_logging.py](japan_avg_hotel_price_finder%2Fconfigure_logging.py)
- Contain logging configuration functions

[graphql_scraper.py](japan_avg_hotel_price_finder%2Fgraphql_scraper.py)
- Contain Basic GraphQL scraper as a function

[whole_mth_graphql_scraper.py](japan_avg_hotel_price_finder%2Fwhole_mth_graphql_scraper.py)
- Contain Whole-Month GraphQL scraper as a function

[migrate_to_sqlite.py](japan_avg_hotel_price_finder%2Fmigrate_to_sqlite.py)
- Migrate data to SQLite table using sqlite3 module.
- Create View using sqlite3 module.

[utils.py](japan_avg_hotel_price_finder%2Futils.py)
- Contain utility functions.

### [graphql_scraper_func](japan_avg_hotel_price_finder%2Fgraphql_scraper_func) Package
[graphql_data_extractor.py](japan_avg_hotel_price_finder%2Fgraphql_scraper_func%2Fgraphql_data_extractor.py)
- Contain functions related to extracting data for GraphQL scrapers

[graphql_data_transformer.py](japan_avg_hotel_price_finder%2Fgraphql_scraper_func%2Fgraphql_data_transformer.py)
- Contain functions related to transforming data for GraphQL scrapers

[graphql_request_func.py](japan_avg_hotel_price_finder%2Fgraphql_scraper_func%2Fgraphql_request_func.py)
- Contain functions related to fetching data from GraphQL endpoint for GraphQL scrapers

[graphql_utils_func.py](japan_avg_hotel_price_finder%2Fgraphql_scraper_func%2Fgraphql_utils_func.py)
- Contain utility functions of GraphQL scrapers

### [check_missing_dates.py](check_missing_dates.py)
- Check the missing dates in the database.

### Automated Hotel Scraper
- Use [automated_scraper.py](automated_scraper.py)
- Scrape Osaka hotel data daily using GitHub action for all 12 months.
- Save to CSV for each month.
- Save CSV to Google Cloud Storage.
