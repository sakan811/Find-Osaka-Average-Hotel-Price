import datetime
import sqlite3

import pytest

from check_missing_dates import scrape_missing_dates
from japan_avg_hotel_price_finder.utils import get_count_of_date_by_mth_asof_today_query


@pytest.mark.asyncio
async def test_scrape_missing_dates() -> None:
    db = 'test_scrape_missing_dates.db'

    today = datetime.datetime.today()
    if today.month == 12:
        month = 1
        year = today.year + 1
    else:
        month = today.month + 1
        year = today.year

    month_str = str(month)
    if len(month_str) == 1:
        month_str = '0' + month_str

    first_missing_date = f'{year}-{month_str}-01'
    second_missing_date = f'{year}-{month_str}-11'
    third_missing_date = f'{year}-{month_str}-20'
    missing_dates = [first_missing_date, second_missing_date, third_missing_date]
    await scrape_missing_dates(missing_dates=missing_dates, is_test=True, test_db=db)

    with sqlite3.connect(db) as con:
        query = get_count_of_date_by_mth_asof_today_query()
        result = con.execute(query).fetchall()
        for row in result:
            assert row[1] == 3


if __name__ == '__main__':
    pytest.main()
