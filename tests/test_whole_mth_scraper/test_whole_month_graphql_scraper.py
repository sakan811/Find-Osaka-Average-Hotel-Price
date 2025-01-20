import datetime
from unittest.mock import patch, AsyncMock

import pandas as pd
import pytest
from freezegun import freeze_time
from pydantic import ValidationError

from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper


@pytest.fixture
def mock_scrape_graphql():
    """Mock the GraphQL scraping which involves network calls."""
    with patch('japan_avg_hotel_price_finder.graphql_scraper.BasicGraphQLScraper.scrape_graphql', new_callable=AsyncMock) as mock:
        # Return a sample DataFrame that matches the expected structure
        mock.return_value = pd.DataFrame({
            'Hotel': ['Test Hotel'],
            'Price': [100],
            'Review': [4.5],
            'Location': ['Test Location'],
            'Price/Review': [22.2],
            'City': ['Osaka'],
            'Date': ['2024-02-01'],
            'AsOf': ['2024-01-17']
        })
        yield mock


@pytest.fixture
def base_params():
    """Common test parameters."""
    return {
        'city': 'Osaka',
        'country': 'Japan',
        'check_in': '',
        'check_out': '',
        'num_rooms': 1,
        'group_adults': 1,
        'group_children': 0,
        'selected_currency': 'USD',
        'scrape_only_hotel': True,
        'nights': 1,
        'start_day': 1
    }


@freeze_time("2024-01-17")  # Freeze time to make tests deterministic
@pytest.mark.asyncio
async def test_scrape_whole_month_success(base_params, mock_scrape_graphql):
    """Test scraping whole month data successfully."""
    # Arrange
    scraper = WholeMonthGraphQLScraper(
        **base_params,
        year=2024,
        month=2  # Use February 2024 (future month) for testing
    )

    # Act
    df = await scraper.scrape_whole_month()

    # Assert
    assert not df.empty, "DataFrame should not be empty"
    assert df.shape[1] == 8, "DataFrame should have 8 columns"
    expected_columns = ['Hotel', 'Price', 'Review', 'Location', 'Price/Review', 'City', 'Date', 'AsOf']
    assert list(df.columns) == expected_columns, "DataFrame should have expected columns"
    
    # Check dates are within February 2024
    dates = pd.to_datetime(df['Date'])
    assert all(date.year == 2024 for date in dates), "All dates should be in 2024"
    assert all(date.month == 2 for date in dates), "All dates should be in February"
    
    # Verify scrape_graphql was called for each day in February
    assert mock_scrape_graphql.call_count == 29  # February 2024 has 29 days


@freeze_time("2024-01-17")
@pytest.mark.asyncio
async def test_scrape_whole_month_past_dates(base_params, mock_scrape_graphql):
    """Test scraping month with past dates returns empty for those dates."""
    # Arrange
    scraper = WholeMonthGraphQLScraper(
        **base_params,
        year=2024,
        month=1  # Current month
    )
    
    # Act
    df = await scraper.scrape_whole_month()
    
    # Assert
    assert not df.empty, "DataFrame should not be empty"
    dates = pd.to_datetime(df['Date'])
    assert all(date >= datetime.datetime(2024, 1, 17).date() for date in dates.dt.date), "Should only have future dates"
    
    # Verify scrape_graphql was called only for future dates
    expected_calls = 31 - 16  # Days remaining in January from 17th
    assert mock_scrape_graphql.call_count == expected_calls


@freeze_time("2024-01-17")
@pytest.mark.asyncio
async def test_scrape_whole_month_empty_result(base_params, mock_scrape_graphql):
    """Test scraping month that's entirely in the past returns empty DataFrame."""
    # Arrange
    scraper = WholeMonthGraphQLScraper(
        **base_params,
        year=2023,
        month=12  # Past month
    )
    
    # Act
    df = await scraper.scrape_whole_month()
    
    # Assert
    assert df.empty, "DataFrame should be empty for past month"
    assert mock_scrape_graphql.call_count == 0, "No scraping should occur for past month"


@pytest.mark.asyncio
async def test_find_last_day_of_month(base_params):
    """Test _find_last_day_of_the_month for different months."""
    test_cases = [
        (2024, 2, 29),  # Leap year February
        (2023, 2, 28),  # Non-leap year February
        (2023, 4, 30),  # 30-day month
        (2023, 12, 31),  # 31-day month
    ]
    
    for year, month, expected_last_day in test_cases:
        scraper = WholeMonthGraphQLScraper(
            **base_params,
            year=year,
            month=month
        )
        last_day = await scraper._find_last_day_of_the_month()
        assert last_day == expected_last_day, f"Last day of {year}-{month} should be {expected_last_day}"


@pytest.mark.parametrize("month", [-1, 0, 13])
def test_invalid_month_validation(base_params, month):
    """Test validation for invalid month values."""
    with pytest.raises(ValidationError) as exc_info:
        WholeMonthGraphQLScraper(
            **base_params,
            year=2024,
            month=month
        )
    error_msg = str(exc_info.value)
    if month <= 0:
        assert "Input should be greater than 0" in error_msg
    else:
        assert "Input should be less than or equal to 12" in error_msg


@pytest.mark.parametrize("year", [-1, 0])
def test_invalid_year_validation(base_params, year):
    """Test validation for invalid year values."""
    with pytest.raises(ValidationError) as exc_info:
        WholeMonthGraphQLScraper(
            **base_params,
            year=year,
            month=1
        )
    assert "Input should be greater than 0" in str(exc_info.value)


@pytest.mark.parametrize("day", [0, 32])
def test_invalid_start_day_validation(base_params, day):
    """Test validation for invalid start day values."""
    with pytest.raises(ValidationError) as exc_info:
        base_params['start_day'] = day
        WholeMonthGraphQLScraper(**base_params)
    error_msg = str(exc_info.value)
    if day <= 0:
        assert "Input should be greater than 0" in error_msg
    else:
        assert "Input should be less than or equal to 31" in error_msg


@pytest.mark.parametrize("nights", [-1, 0])
def test_invalid_nights_validation(base_params, nights):
    """Test validation for invalid number of nights."""
    with pytest.raises(ValidationError) as exc_info:
        base_params['nights'] = nights
        WholeMonthGraphQLScraper(**base_params)
    assert "Input should be greater than 0" in str(exc_info.value)


@pytest.mark.parametrize("field", ['city', 'country'])
def test_invalid_type_validation(base_params, field):
    """Test validation for invalid field types (None values)."""
    with pytest.raises(ValidationError) as exc_info:
        base_params[field] = None
        WholeMonthGraphQLScraper(**base_params)
    assert "Input should be a valid string" in str(exc_info.value)


@pytest.mark.parametrize("field", ['city', 'country'])
def test_empty_string_validation(base_params, field):
    """Test validation for empty string fields."""
    # First modify the model to enforce non-empty strings
    original_value = base_params[field]
    base_params[field] = ''
    
    # Test empty string validation
    with pytest.raises(ValidationError) as exc_info:
        WholeMonthGraphQLScraper(**base_params)
    assert "String should have at least 1 character" in str(exc_info.value)
    
    # Restore original value
    base_params[field] = original_value