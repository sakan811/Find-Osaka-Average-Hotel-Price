import pytest
from pydantic import ValidationError
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper


def test_validate_inputs_success():
    """Test validation succeeds with valid inputs"""
    scraper = BasicGraphQLScraper(
        city="Tokyo",
        country="Japan",
        check_in="2024-07-05",
        check_out="2024-07-06",
        group_adults=1,
        num_rooms=1,
        group_children=0,
        selected_currency="USD",
        scrape_only_hotel=True
    )
    assert scraper._validate_inputs() is True


@pytest.mark.parametrize("field,value", [
    ("check_in", ""),
    ("check_out", ""),
    ("selected_currency", "")
])
def test_validate_inputs_empty_optional(field, value):
    """Test validation fails with empty optional fields"""
    params = {
        "city": "Tokyo",
        "country": "Japan",
        "check_in": "2024-07-05",
        "check_out": "2024-07-06",
        "group_adults": 1,
        "num_rooms": 1,
        "group_children": 0,
        "selected_currency": "USD",
        "scrape_only_hotel": True
    }
    params[field] = value
    scraper = BasicGraphQLScraper(**params)
    assert scraper._validate_inputs() is False


@pytest.mark.parametrize("field", ["city", "country"])
def test_validate_inputs_empty_required(field):
    """Test validation fails with empty required fields"""
    params = {
        "city": "Tokyo",
        "country": "Japan",
        "check_in": "2024-07-05",
        "check_out": "2024-07-06",
        "group_adults": 1,
        "num_rooms": 1,
        "group_children": 0,
        "selected_currency": "USD",
        "scrape_only_hotel": True
    }
    params[field] = ""
    with pytest.raises(ValidationError) as exc_info:
        BasicGraphQLScraper(**params)
    assert "String should have at least 1 character" in str(exc_info.value)