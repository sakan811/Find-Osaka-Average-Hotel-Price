# Find the Hotel's Average Room Price in Osaka 

Showcase visualizations about the Hotel's Average Room Price in Osaka.

## Status
[![CodeQL](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml)    
[![Scraper Test](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml)  
[![Scrape](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml)

## Visualizations
[Power BI](https://app.powerbi.com/view?r=eyJrIjoiOGFiNzQ1Y2UtZTVlOS00MzkyLTlmN2EtMDY2YWVlNzFiNTIyIiwidCI6ImZlMzViMTA3LTdjMmYtNGNjMy1hZDYzLTA2NTY0MzcyMDg3OCIsImMiOjEwfQ%3D%3D)  

Data as of June 7, 2024  
[Instagram](https://www.instagram.com/p/C77ANT0M3ni/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==)  
[Facebook](https://www.facebook.com/permalink.php?story_fbid=pfbid027P3bgdRAnAsN9iE2ioHihufPHKrcL626evEVKF8ytFhX4WbDvazACVfQeMK5zJ7ml&id=61553626169836)

## Project Details
Collect Osaka hotel property data from Booking.com

Data collecting start date: May 16th, 2024.

Data was collected daily using GitHub action.

This script can also be used to scrape data from other cities.

## Code Base Details 
### To scrape hotel data
- Go to [set_details.py](set_details.py)
- Set the parameters of the 'Details' dataclass as needed.
  - Example:
  ```
  # Set booking details.
  city: str = 'Osaka'  # city where the hotels are located.
  
  # Check-in and Check-out are used only when using the Basic Scraper
  check_in: str = '2024-12-01'
  check_out: str = '2024-12-12'
  
  group_adults: int = 1  # number of adults
  num_rooms: int = 1  # number of rooms
  group_children: int = 0  # number of children
  selected_currency: str = 'USD'  # currency of the room price
  
  # Optional
  # Set the start date and number of nights when using Thread Pool Scraper
  start_day: int = 1  # day to start scraping
  month: int = 12  # month to start scraping
  year: int = 2024  # year to start scraping
  nights: int = 1  # number of night to scrape. this determines the room price of the hotels.
   
  # Set SQLite database name
  sqlite_name: str = 'test.db'
  ```
- To scrape using Thread Pool Scraper:
  - Run the following command via command line terminal:
    ```  
    python main.py --thread_pool=True
    ```
  - Scrape data start from the given start date to the end of the same month.
    - Scrape nine dates at the same time.
    - To specify the dates to be scraped at the same time, add ```--workers```
      - For example, the following command line set the Thread Pool Scraper to scrape five dates at the same time. 
      ```
      python main.py --thread_pool=True --workers=5
      ```
- To scrape using Basic Scraper:
  - Run the following command via command line terminal:
    ```  
    python main.py 
    ```
  - Scrape data based on the given check-in and check-out date.
- Data is saved to CSV by default.
  - CSV is saved to 'scraped_hotel_data_csv' folder. 
- Add ```--to_sqlite=True``` to save data to SQLite database.
  ```  
  python main.py --to_sqlite=True
  ```
- Month to scrape can be specified using ```--month=(month number as int)``` for Thread Pool.
  - For example, to scrape data from June of the current year using Thread Pool Scraper, run the following command line:
  ```  
  python main.py --thread_pool=True --month=6
  ``` 
  - Be careful with 'start_day' variable in [set_details.py](set_details.py), 
  as using --month will make the scraper starts from the day specified in 'start_day' variable 
  in [set_details.py](set_details.py) 

### To find the missing dates in the database or in the CSV files directory
To ensure that all dates of the month were scraped when using the Thread Pool scraper, functions in
[check_missing_dates.py](check_missing_dates.py) will check in the given SQLite database or CSV files directory
to find the missing dates.
- To check in the database, use the following command line as an example:
  ```  
  python check_missing_dates.py --check_db=hotel_data.db
  ``` 
  - ```--check_db``` should be follow by the path of the database, without any quote.
- To check in the CSV files directory, use the following command line as an example:
  ```  
  python check_missing_dates.py --check_csv=scraped_hotel_data_csv
  ``` 
  - ```--check_csv``` should be follow by the path of the CSV files directory, without any quote.
- If there are missing dates, a Basic Scraper will automatically start to scrape those dates.
- Only check the missing dates of the data that was scraped today.

### Dataclass
[set_details.py](set_details.py)
- Dataclass that stores booking details, date, and length of stay.
  - Provide which kind of hotel data to scrape.
  
### [japan_avg_hotel_price_finder](japan_avg_hotel_price_finder) Package
[migrate_to_sqlite.py](japan_avg_hotel_price_finder%2Fmigrate_to_sqlite.py)
- Migrate data to SQLite table using sqlite3 module.
  - Create SQLite database named 'avg_japan_hotel_price.db'
- Create View using sqlite3 module.

[scrape.py](japan_avg_hotel_price_finder%2Fscrape.py)
- Scrape data from Booking.com website.

[thread_scrape.py](japan_avg_hotel_price_finder%2Fthread_scrape.py)
- Scrape data for five dates at the same time using Thread Pool Execute.
  - Start from the given start date until the end of the same month.

[utils.py](japan_avg_hotel_price_finder%2Futils.py)
- Contain utility functions.

### [check_missing_dates.py](check_missing_dates.py)
- Check the missing dates in the database or in the CSV files directory.

### Automated Hotel Scraper
- Scrape Osaka hotel data daily using GitHub action for all 12 months.
  - Use the GraphQL scraper from [use_graphql_scraper.py](use_graphql_scraper.py) with --month for each month.
- Save to CSV for each month.
- Save CSV to Google Cloud Storage.
