import datetime
from unittest.mock import patch
import pytest
from sqlalchemy import create_engine, text, Table, Column, Integer, String, Float, TIMESTAMP, MetaData
import pandas as pd

from japan_avg_hotel_price_finder.japan_hotel_scraper import JapanScraper


@pytest.mark.asyncio
async def test_japan_scraper(tmp_path):
    # Create a test database
    db = str(tmp_path / 'test_japan_scraper.db')
    engine = create_engine(f'sqlite:///{db}')

    # Create the table explicitly with correct column names matching the model
    metadata = MetaData()
    Table('JapanHotels', metadata,
          Column('ID', Integer, primary_key=True, autoincrement=True),
          Column('Hotel', String, nullable=False),
          Column('Price', Float, nullable=False),
          Column('Review', Float, nullable=False),
          Column('Price/Review', Float, nullable=False),
          Column('Date', String, nullable=False),
          Column('Region', String, nullable=False),
          Column('Prefecture', String, nullable=False),
          Column('Location', String, nullable=False),
          Column('AsOf', TIMESTAMP, nullable=False)
        )
    metadata.create_all(engine)

    # Mock current date for consistent testing
    current_date = datetime.datetime(2024, 1, 1)
    check_in = (current_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    check_out = (current_date + datetime.timedelta(days=2)).strftime("%Y-%m-%d")

    # Create scraper instance with test configuration
    scraper = JapanScraper(
        engine=engine,
        country='Japan',
        city='Hokkaido',
        check_in=check_in,
        check_out=check_out,
        group_adults=1,
        num_rooms=1,
        group_children=0,
        selected_currency='USD',
        scrape_only_hotel=True
    )
    scraper.japan_regions = {"Hokkaido": ["Hokkaido"]}  # Simplified regions for testing

    # Mock the scrape_whole_year method
    async def mock_scrape_whole_year():
        # Create test data with correct column names
        df = pd.DataFrame({
            'Hotel': ['Test Hotel'],
            'Price': [100.0],
            'Review': [4.5],
            'Location': ['Test Location'],
            'Price/Review': [22.2],
            'Prefecture': ['Hokkaido'],
            'Date': [check_in],
            'AsOf': [current_date],
            'Region': ['Hokkaido']
        })
        scraper._load_to_database(df)

    # Patch the _scrape_whole_year method
    with patch.object(scraper, '_scrape_whole_year', new=mock_scrape_whole_year):
        await scraper.scrape_japan_hotels()

    # Verify data was inserted correctly
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM JapanHotels")).fetchall()
        assert len(result) == 1
        assert result[0].Hotel == 'Test Hotel'
        assert result[0].Price == 100.0
        assert result[0].Review == 4.5
        assert result[0].Region == 'Hokkaido'
        assert result[0].Prefecture == 'Hokkaido'
        assert result[0].Location == 'Test Location'
        assert getattr(result[0], 'Price/Review') == 22.2