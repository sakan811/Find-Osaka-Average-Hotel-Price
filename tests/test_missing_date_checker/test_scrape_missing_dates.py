import datetime

import pytest
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from check_missing_dates import scrape_missing_dates, BookingDetails
from japan_avg_hotel_price_finder.sql.db_model import Base, HotelPrice


@pytest.mark.asyncio
async def test_scrape_missing_dates(tmp_path) -> None:
    db_file = tmp_path / "test_scrape_missing_dates.db"
    db_url = f'sqlite:///{db_file}'
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    booking_details_param = BookingDetails(city='Osaka', group_adults=1, num_rooms=1, group_children=0,
                                           selected_currency='USD', scrape_only_hotel=True, sqlite_name=str(db_file))

    today = datetime.datetime.today()
    if today.month == 12:
        month = 1
        year = today.year + 1
    else:
        month = today.month + 1
        year = today.year

    month_str = str(month).zfill(2)

    first_missing_date = f'{year}-{month_str}-01'
    second_missing_date = f'{year}-{month_str}-11'
    third_missing_date = f'{year}-{month_str}-20'
    missing_dates = [first_missing_date, second_missing_date, third_missing_date]

    await scrape_missing_dates(missing_dates_list=missing_dates, booking_details_class=booking_details_param)

    session = Session()
    try:
        result = (
            session.query(func.strftime('%Y-%m', HotelPrice.Date).label('month'),
                          func.count(func.distinct(HotelPrice.Date)).label('count'))
            .filter(HotelPrice.City == 'Osaka')
            .filter(func.date(HotelPrice.AsOf) == func.date('now'))
            .group_by(func.strftime('%Y-%m', HotelPrice.Date))
            .all()
        )

        assert len(result) == 1  # We expect only one month
        assert result[0].count == 3  # We expect 3 dates to be scraped
    finally:
        session.close()

    # Clean up: drop all tables
    Base.metadata.drop_all(engine)


if __name__ == '__main__':
    pytest.main()