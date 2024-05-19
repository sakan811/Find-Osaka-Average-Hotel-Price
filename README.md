# Find the Hotel's Average Room Price in Osaka by Date

Showcase visualizations about the Hotel's Average Room Price in Osaka.

## Project Details
Collect Osaka hotel property data from Booking.com

Data collecting start date: May 16th, 2024.

Data was collected daily using GitHub action and [daily_scraper.py](daily_scraper.py)

This script can also be used to scrape data from other cities.

## Code Base Details
### To scrape hotel data
- Go to [main.py](main.py)
- Set the following booking details parameters to scrape the hotel with specified data 
```
# Define booking parameters for the hotel search.
city = 'Osaka'  # Specify the city for the hotel search.
group_adults = '1'  # Number of adults per room.
num_rooms = '1'  # Number of rooms to book.
group_children = '0'  # Number of children per room.
selected_currency = 'USD'  # Currency for the booking prices.
```
- Set the following date and length of stay parameters to scrape the hotel with specified data
```
# Specify the start date and duration of stay for data scraping
start_day = 17  # The day of the month to start scraping data.
month = 5  # The month to start scraping data.
year = 2024  # The year to start scraping data.
nights = 1  # Number of nights for the stay.
```
- Run the script

### [japan_avg_hotel_price_finder](japan_avg_hotel_price_finder) Package
[migrate_to_sqlite.py](japan_avg_hotel_price_finder%2Fmigrate_to_sqlite.py)
- Migrate data to SQLite table using sqlite3 module.
  - Create SQLite database named 'avg_japan_hotel_price.db'
- Create View using sqlite3 module.

[scrape.py](japan_avg_hotel_price_finder%2Fscrape.py)
- Scrape data from Booking.com website.

[scrape_each_date.py](japan_avg_hotel_price_finder%2Fscrape_each_date.py)
- Scrape data for each date.
  - Start from the given start date until the end of the same month.

[thread_scrape.py](japan_avg_hotel_price_finder%2Fthread_scrape.py)
- Scrape data for five dates at the same time using Thread Pool Execute.
  - Start from the given start date until the end of the same month.

### Daily Hotel Scraper
[daily_scraper.py](daily_scraper.py)
- Scrape Osaka hotel data daily using GitHub action for all 12 months.
  - Save to CSV for each month.
- Send CSV via email.
- Big thanks to https://yasoob.me/posts/github-actions-web-scraper-schedule-tutorial/