import datetime
import pytz

import pytest
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker

from check_missing_dates import scrape_missing_dates
from japan_avg_hotel_price_finder.booking_details import BookingDetails
from japan_avg_hotel_price_finder.sql.db_model import HotelPrice, Base


@pytest.mark.asyncio
async def test_scrape_missing_dates(tmp_path) -> None:
    db_file = tmp_path / "test_scrape_missing_dates.db"
    db_url = f'sqlite:///{db_file}'
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    booking_details_param = BookingDetails(city='Osaka', group_adults=1, num_rooms=1, group_children=0,
                                           selected_currency='USD', scrape_only_hotel=True)

    today = datetime.datetime.now(pytz.UTC)
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    year, month = next_month.year, next_month.month

    month_str = str(month).zfill(2)

    missing_dates = [
        f'{year}-{month_str}-01',
        f'{year}-{month_str}-11',
        f'{year}-{month_str}-20'
    ]

    await scrape_missing_dates(missing_dates_list=missing_dates, booking_details_class=booking_details_param,
                               engine=engine)

    session = Session()
    try:
        # Get the AsOf date from the first record
        asof_date = session.query(func.date(HotelPrice.AsOf)).first()[0]

        result = (
            session.query(func.strftime('%Y-%m', HotelPrice.Date).label('month'),
                          func.count(func.distinct(HotelPrice.Date)).label('count'))
            .filter(HotelPrice.City == 'Osaka')
            .filter(func.date(HotelPrice.AsOf) == asof_date)
            .group_by(func.strftime('%Y-%m', HotelPrice.Date))
            .all()
        )

        print(f"Query result: {result}")

        assert len(result) == 1, f"Expected 1 result, but got {len(result)}"
        assert result[0].count == 3, f"Expected 3 dates, but got {result[0].count if result else 'no results'}"
    finally:
        session.close()

    # Clean up: drop all tables
    Base.metadata.drop_all(engine)