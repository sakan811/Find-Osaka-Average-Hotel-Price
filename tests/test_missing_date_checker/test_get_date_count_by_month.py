import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from check_missing_dates import get_date_count_by_month, HotelPrice


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    HotelPrice.metadata.create_all(engine)
    return Session()


def test_get_date_count_by_month_single_month(session):
    # Arrange
    city = "Tokyo"
    today = datetime(2024, 11, 15).date()  # Set a fixed date in the middle of the month
    today_str = today.strftime('%Y-%m-%d')

    session.add(HotelPrice(
        Hotel="Test Hotel",
        Price=100.0,
        Review=4.5,
        Location="Test Location",
        PriceReview=22.22,
        City=city,
        Date=today_str,
        AsOf=today
    ))
    session.add(HotelPrice(
        Hotel="Test Hotel 2",
        Price=150.0,
        Review=4.0,
        Location="Test Location 2",
        PriceReview=37.5,
        City=city,
        Date=today_str,
        AsOf=today
    ))
    session.add(HotelPrice(
        Hotel="Test Hotel 3",
        Price=200.0,
        Review=4.8,
        Location="Test Location 3",
        PriceReview=41.67,
        City=city,
        Date=(today + timedelta(days=1)).strftime('%Y-%m-%d'),
        AsOf=today
    ))
    session.commit()

    # Act
    result = get_date_count_by_month(session, city, as_of=today)

    # Assert
    assert len(result) == 1
    assert result[0][0] == '2024-11'  # Check that the month is correct
    assert result[0][1] == 2  # Check that the count is correct (2 distinct dates in November)


def test_get_date_count_by_month_multiple_cities(session):
    # Arrange
    city1, city2 = "Tokyo", "Osaka"
    today = datetime.today().date()
    session.add(HotelPrice(
        City=city1,
        Date=today,
        AsOf=today,
        Hotel="Hotel1",
        Price=100.0,
        Review=4.5,
        Location="Test Location 1",
        PriceReview=22.22
    ))
    session.add(HotelPrice(
        City=city2,
        Date=today,
        AsOf=today,
        Hotel="Hotel2",
        Price=150.0,
        Review=4.0,
        Location="Test Location 2",
        PriceReview=37.5
    ))
    session.commit()

    # Act
    result1 = get_date_count_by_month(session, city1)
    result2 = get_date_count_by_month(session, city2)

    # Assert
    assert len(result1) == 1 and len(result2) == 1
    assert result1[0][1] == 1 and result2[0][1] == 1


def test_get_date_count_by_month_no_data(session):
    # Arrange
    city = "Tokyo"

    # Act
    result = get_date_count_by_month(session, city)

    # Assert
    assert len(result) == 0


def test_get_date_count_by_month_multiple_months(session):
    # Arrange
    city = "Tokyo"
    today = datetime.today().date()
    next_month = today.replace(month=today.month % 12 + 1)
    session.add(HotelPrice(
        City=city,
        Date=today,
        AsOf=today,
        Hotel="Hotel1",
        Price=100.0,
        Review=4.5,
        Location="Test Location 1",
        PriceReview=22.22
    ))
    session.add(HotelPrice(
        City=city,
        Date=next_month,
        AsOf=today,
        Hotel="Hotel2",
        Price=150.0,
        Review=4.0,
        Location="Test Location 2",
        PriceReview=37.5
    ))
    session.commit()

    # Act
    result = get_date_count_by_month(session, city)

    # Assert
    assert len(result) == 2
    assert set(month for month, _ in result) == {today.strftime('%Y-%m'), next_month.strftime('%Y-%m')}
    assert all(count == 1 for _, count in result)
