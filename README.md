# Find the Hotel's Average Room Price in Osaka 

Showcase visualizations about the Hotel's Average Room Price in Osaka.

## Status
[![CodeQL](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/codeql.yml)    
[![Scraper Test](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scraper-test.yml)  
[![Scrape](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml/badge.svg)](https://github.com/sakan811/Find-Osaka-Average-Hotel-Price/actions/workflows/scrape.yml)

## Visualizations
[Power BI](https://app.powerbi.com/view?r=eyJrIjoiOGFiNzQ1Y2UtZTVlOS00MzkyLTlmN2EtMDY2YWVlNzFiNTIyIiwidCI6ImZlMzViMTA3LTdjMmYtNGNjMy1hZDYzLTA2NTY0MzcyMDg3OCIsImMiOjEwfQ%3D%3D)  

Data as of May 19, 2024  
[Instagram](https://www.instagram.com/p/C7J1Uy0uuDK/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==)  
[Facebook](https://www.facebook.com/permalink.php?story_fbid=pfbid0VY15MZY5RAPoE7xW5nHEaLhF9SC1kgt2eyiyg5xRZ35MynJpVA1Yi5fWwhTwa7rzl&id=61553626169836)

## Project Details
Collect Osaka hotel property data from Booking.com

Data collecting start date: May 16th, 2024.

Data was collected weekly using GitHub action with [automated_scraper.py](automated_scraper.py)

This script can also be used to scrape data from other cities.

## Code Base Details 
### To scrape hotel data
- Go to [set_details.py](set_details.py)
- Set the parameters of the 'Details' dataclass as needed.
  - Example:
  ```
  # Set booking details.
  city: str = 'Osaka'
  
  # Check-in and Check-out are used only when using the Basic Scraper
  check_in: str = '2024-12-01'
  check_out: str = '2024-12-12'
  
  group_adults: int = 1
  num_rooms: int = 1
  group_children: int = 0
  selected_currency: str = 'USD'
  
  # Optional
  # Set the start date and number of nights when using Thread Pool Scraper or Month End Scraper
  start_day: int = 1
  month: int = 12
  year: int = 2024
  nights: int = 1
  
  # Set SQLite database name
  sqlite_name: str = 'test.db'
  ```
- To scrape using Thread Pool Scraper:
  - Run the following command via command line terminal:
    ```  
    python main.py --thread_pool=True
    ```
  - Scrape data start from the given start date to the end of the same month.
    - Scrape five dates at the same time.
- To scrape using Month End Scraper:
  - Run the following command via command line terminal:
    ```  
    python main.py --month_end=True
    ```
  - Scrape data start from the given start date to the end of the same month.
- To scrape using Basic Scraper:
  - Run the following command via command line terminal:
    ```  
    python main.py 
    ```
  - Scrape data based on the given check-in and check-out date.
- Data is saved to CSV by default.
  - Add ```--to_sqlite=True``` to save data to SQLite database.
  ```  
  python main.py --to_sqlite=True
  ```
    
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

[scrape_until_month_end.py](japan_avg_hotel_price_finder%2Fscrape_until_month_end.py)
- Scrape data for each date.
  - Start from the given start date until the end of the same month.

[thread_scrape.py](japan_avg_hotel_price_finder%2Fthread_scrape.py)
- Scrape data for five dates at the same time using Thread Pool Execute.
  - Start from the given start date until the end of the same month.

[utils.py](japan_avg_hotel_price_finder%2Futils.py)
- Contain utility functions.

### Automated Hotel Scraper
[automated_scraper.py](automated_scraper.py)
- Scrape Osaka hotel data daily using GitHub action for all 12 months.
  - Save to CSV for each month.
- Save CSV to Google Cloud Storage
