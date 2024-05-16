# Find the Hotel's Average Room Price in Osaka by Date

Collect data from Booking.com

Data collecting start date: May 16th, 2024.

## [japan_avg_hotel_price_finder](japan_avg_hotel_price_finder) Package
[migrate_to_sqlite.py](japan_avg_hotel_price_finder%2Fmigrate_to_sqlite.py)
- Migrate data to SQLite table using sqlite3 module.
- Create View using sqlite3 module.

[scrape.py](japan_avg_hotel_price_finder%2Fscrape.py)
- Scrape data from Booking.com website.

[scrape_each_date.py](japan_avg_hotel_price_finder%2Fscrape_each_date.py)
- Scrape data for each date.
  - Start from the given start date until the end of the same month.