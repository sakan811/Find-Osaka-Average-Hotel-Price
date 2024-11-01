import datetime
from unittest.mock import patch, AsyncMock

import pytest
from sqlalchemy import create_engine, text, Table, Column, Integer, String, Date, Boolean, MetaData
import pandas as pd

from japan_avg_hotel_price_finder.japan_hotel_scraper import JapanScraper


@pytest.mark.asyncio
async def test_japan_scraper(tmp_path):
    db = str(tmp_path / 'test_japan_scraper.db')
    engine = create_engine(f'sqlite:///{db}')

    # Create the table explicitly
    metadata = MetaData()
    Table('JapanHotels', metadata,
          Column('id', Integer, primary_key=True),
          Column('Region', String),
          Column('Prefecture', String),
          Column('hotel_name', String),
          Column('price', Integer),
          Column('date', Date),
          Column('check_in', String),
          Column('check_out', String),
          Column('group_adults', Integer),
          Column('num_rooms', Integer),
          Column('group_children', Integer),
          Column('selected_currency', String),
          Column('scrape_only_hotel', Boolean),
          Column('country', String),
          Column('city', String)
          )
    metadata.create_all(engine)

    scraper = JapanScraper(
        engine=engine,
        country='Japan',
        city='',
        check_in='',
        check_out='',
        group_adults=1,
        num_rooms=1,
        group_children=0,
        selected_currency='USD',
        scrape_only_hotel=True
    )
    scraper.japan_regions = {"Hokkaido": ["Hokkaido"]}
    current_month = datetime.datetime.now().month
    scraper.start_month = current_month
    scraper.end_month = current_month

    # Create sample data
    sample_data = pd.DataFrame({
        'Region': ['Hokkaido', 'Hokkaido'],
        'Prefecture': ['Hokkaido', 'Hokkaido'],
        'hotel_name': ['Hotel A', 'Hotel B'],
        'price': [100, 200],
        'date': [datetime.date(2023, current_month, 1), datetime.date(2023, current_month, 2)],
        'check_in': ['2023-11-01', '2023-11-02'],
        'check_out': ['2023-11-02', '2023-11-03'],
        'group_adults': [1, 1],
        'num_rooms': [1, 1],
        'group_children': [0, 0],
        'selected_currency': ['USD', 'USD'],
        'scrape_only_hotel': [True, True],
        'country': ['Japan', 'Japan'],
        'city': ['Hokkaido', 'Hokkaido']
    })

    # Insert sample data directly into the database
    sample_data.to_sql('JapanHotels', engine, if_exists='append', index=False)

    # Mock the _scrape_whole_year method to return our sample data
    async def mock_scrape_whole_year():
        return sample_data

    with patch.object(JapanScraper, '_scrape_whole_year',
                      new=AsyncMock(side_effect=mock_scrape_whole_year)) as mock_scrape:
        await scraper.scrape_japan_hotels()

    # Check if the mock was called
    assert mock_scrape.called, "_scrape_whole_year was not called"
    mock_scrape.assert_called_once()

    # Verify data in the database
    with engine.connect() as conn:
        # Check if the table exists
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='JapanHotels'"))
        assert result.fetchone() is not None, "JapanHotels table does not exist"

        # Check the number of rows
        result = conn.execute(text("SELECT COUNT(*) FROM JapanHotels"))
        count = result.scalar()
        assert count == 2, f"Expected 2 rows in the database, but found {count}"

        # Check the content of the rows
        result = conn.execute(text("SELECT * FROM JapanHotels"))
        rows = result.fetchall()

        for i, row in enumerate(rows):
            assert row.Region == 'Hokkaido', f"Row {i}: Region mismatch"
            assert row.Prefecture == 'Hokkaido', f"Row {i}: Prefecture mismatch"
            assert row.hotel_name == f'Hotel {"A" if i == 0 else "B"}', f"Row {i}: hotel_name mismatch"
            assert row.price == (100 if i == 0 else 200), f"Row {i}: price mismatch"
            assert row.date == f'2023-11-0{i + 1}', f"Row {i}: date mismatch"
            assert row.check_in == f'2023-11-0{i + 1}', f"Row {i}: check_in mismatch"
            assert row.check_out == f'2023-11-0{i + 2}', f"Row {i}: check_out mismatch"
            assert row.group_adults == 1, f"Row {i}: group_adults mismatch"
            assert row.num_rooms == 1, f"Row {i}: num_rooms mismatch"
            assert row.group_children == 0, f"Row {i}: group_children mismatch"
            assert row.selected_currency == 'USD', f"Row {i}: selected_currency mismatch"
            assert row.scrape_only_hotel == 1, f"Row {i}: scrape_only_hotel mismatch"  # SQLite stores booleans as 0 or 1
            assert row.country == 'Japan', f"Row {i}: country mismatch"
            assert row.city == 'Hokkaido', f"Row {i}: city mismatch"

    print("Test completed successfully!")