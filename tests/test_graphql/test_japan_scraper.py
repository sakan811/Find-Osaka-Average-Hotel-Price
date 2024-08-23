import asyncio
import datetime

import duckdb

from japan_hotel_scraper import JapanScraper


def test_japan_scraper():
    db = 'test_japan_scraper.duckdb'

    scraper = JapanScraper(duckdb_path=db, country='Japan', city='', check_in='', check_out='', sqlite_name='')
    scraper.japan_regions = {"Hokkaido": ["Hokkaido"]}
    current_month = datetime.datetime.now().month
    scraper.start_month = current_month
    scraper.end_month = current_month
    asyncio.run(scraper.scrape_japan_hotels())

    with duckdb.connect(db) as conn:
        res = conn.execute('SELECT * FROM JapanHotels').fetchall()
        assert len(res) > 1
