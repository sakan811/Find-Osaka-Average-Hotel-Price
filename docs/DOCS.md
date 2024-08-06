# Brief Script Documents
## Dataclass
[set_details.py](set_details.py)
- A **dataclass** designed to encapsulate various **parameters** required for **scraping** hotel data.
  - The **parameters** are booking details, e.g., city, check-in, check-out, etc.
  
## [japan_avg_hotel_price_finder](japan_avg_hotel_price_finder) Package
[configure_logging.py](japan_avg_hotel_price_finder%2Fconfigure_logging.py)
- Contain logging configuration functions
- You can set the logging level in this script:
  ```
  main_logger = configure_logging_with_file(log_dir='logs', log_file='main.log', logger_name='main', level="INFO")
  ```

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

## [check_missing_dates.py](check_missing_dates.py)
- Check the missing dates in the database.

## Automated Hotel Scraper
- Use [automated_scraper.py](automated_scraper.py)
- Scrape Osaka hotel data daily using GitHub action for all 12 months.
- Save to CSV for each month.
- Save CSV to Google Cloud Storage.
