import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from freezegun import freeze_time
import datetime
import pandas as pd

from check_missing_dates import scrape_missing_dates
from japan_avg_hotel_price_finder.booking_details import BookingDetails
from japan_avg_hotel_price_finder.sql.db_model import HotelPrice, Base
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.sql.save_to_db import save_scraped_data


@pytest.mark.asyncio
@freeze_time("2024-01-15 12:00:00", tz_offset=0)
async def test_scrape_missing_dates(tmp_path) -> None:
    db_file = tmp_path / "test_scrape_missing_dates.db"
    db_url = f'sqlite:///{db_file}'
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    # First, populate the database with some existing dates
    existing_dates = [
        '2024-02-02',
        '2024-02-03',
        '2024-02-04',
        '2024-02-05',
        '2024-02-06',
        '2024-02-07',
        '2024-02-08',
        '2024-02-09',
        '2024-02-10',
        '2024-02-12',
        '2024-02-13',
        '2024-02-14',
        '2024-02-15',
        '2024-02-16',
        '2024-02-17',
        '2024-02-18',
        '2024-02-19',
    ]

    # Create sample data for existing dates
    existing_data = []
    asof_date = datetime.datetime(2024, 1, 15)
    for date in existing_dates:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        existing_data.append({
            'Hotel': 'Test Hotel',
            'Price': 100.0,
            'Review': 8.5,
            'City': 'Osaka',
            'Date': date_obj.date(),  # Convert to date object
            'AsOf': asof_date.date(),  # Convert to date object
            'Location': 'Test Address',  # Add Location field
            'PriceReview': 100.0 / 8.5  # Add PriceReview field
        })
    
    df = pd.DataFrame(existing_data)
    
    # Convert DataFrame columns to datetime.date objects
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df['AsOf'] = pd.to_datetime(df['AsOf']).dt.date
    
    save_scraped_data(df, engine)

    booking_details_param = BookingDetails(city='Osaka', group_adults=1, num_rooms=1, group_children=0,
                                           selected_currency='USD', scrape_only_hotel=True, country='Japan')

    # These are the dates that should be identified as missing
    missing_dates = [
        '2024-02-01',  # Missing at start
        '2024-02-11',  # Missing in middle
        '2024-02-20'   # Missing at end
    ]

    # Mock response data for each date
    def create_mock_data(check_in):
        check_in_date = datetime.datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = check_in_date + datetime.timedelta(days=1)
        check_out = check_out_date.strftime('%Y-%m-%d')
        
        return {
            'data': {
                'searchQueries': {
                    'search': {
                        'appliedFilterOptions': [{'name': 'popular_filters', 'urlId': 'ht_id=204'}],
                        'pagination': {'nbResultsTotal': 1},
                        'breadcrumbs': [
                            {'name': 'Japan', 'destType': 'COUNTRY'},
                            {'name': 'Osaka', 'destType': 'CITY'}
                        ],
                        'flexibleDatesConfig': {
                            'dateRangeCalendar': {
                                'checkin': [check_in],
                                'checkout': [check_out]
                            }
                        },
                        'searchMeta': {
                            'nbAdults': 1,
                            'nbChildren': 0,
                            'nbRooms': 1
                        },
                        'results': [{
                            'displayName': {'text': 'Test Hotel'},
                            'basicPropertyData': {
                                'reviewScore': {'score': 8.5}
                            },
                            'blocks': [{
                                'finalPrice': {
                                    'amount': 100.0,
                                    'currency': 'USD'
                                }
                            }],
                            'location': {'displayLocation': 'Test Address'}
                        }]
                    }
                }
            }
        }

    # Create mock response and session
    def create_mock_session(check_in):
        mock_data = create_mock_data(check_in)
        
        # Create mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_data)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        # Create mock session
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        return mock_session, mock_data

    # Keep track of current date being processed
    current_date = None

    def get_mock_session():
        nonlocal current_date
        session, data = create_mock_session(current_date)
        BasicGraphQLScraper.data = data
        return session

    # Patch all necessary methods
    with patch('aiohttp.ClientSession', side_effect=get_mock_session), \
         patch.object(BasicGraphQLScraper, '_find_total_page_num', return_value=1), \
         patch.object(BasicGraphQLScraper, '_check_city_data', return_value='Osaka'), \
         patch.object(BasicGraphQLScraper, '_check_country_data', return_value='Japan'), \
         patch.object(BasicGraphQLScraper, '_check_currency_data', return_value='USD'), \
         patch.object(BasicGraphQLScraper, '_check_hotel_filter_data', return_value=True):
        
        for date in missing_dates:
            current_date = date
            await scrape_missing_dates([date], booking_details_class=booking_details_param,
                                   engine=engine)

    session = Session()
    try:
        # Get all dates in the database for Osaka
        dates_in_db = (
            session.query(func.date(HotelPrice.Date))
            .filter(HotelPrice.City == 'Osaka')
            .distinct()
            .order_by(HotelPrice.Date)
            .all()
        )
        # Convert the date objects to strings in YYYY-MM-DD format
        dates_in_db = [datetime.datetime.strptime(str(d[0]), '%Y-%m-%d').strftime('%Y-%m-%d') for d in dates_in_db]

        # Verify all dates are present (both existing and previously missing)
        all_expected_dates = sorted(existing_dates + missing_dates)
        assert dates_in_db == all_expected_dates, f"Expected all dates to be present. Missing: {set(all_expected_dates) - set(dates_in_db)}"

        # Verify the count of dates for February 2024
        feb_2024_count = (
            session.query(func.count(func.distinct(HotelPrice.Date)))
            .filter(HotelPrice.City == 'Osaka')
            .filter(func.strftime('%Y-%m', HotelPrice.Date) == '2024-02')
            .scalar()
        )
        assert feb_2024_count == 20, f"Expected 20 dates for February 2024, but got {feb_2024_count}"

    finally:
        session.close()

    # Clean up: drop all tables
    Base.metadata.drop_all(engine)