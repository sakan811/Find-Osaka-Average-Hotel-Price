import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from check_missing_dates import get_dates_in_db, HotelPrice


@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    HotelPrice.metadata.create_all(engine)
    session = Session()
    yield session
    session.close()


def test_get_dates_in_db_returns_correct_dates(db_session):
    # Arrange
    today = datetime.now().date()
    city = "TestCity"
    dates = [today, today + timedelta(days=1), today + timedelta(days=2)]
    for date in dates:
        db_session.add(HotelPrice(
            Hotel="Test Hotel",  # Add a non-null value for Hotel
            Price=100.0,  # Add a non-null value for Price
            Review=4.5,  # Add a non-null value for Review
            Location="Test Location",  # Add a non-null value for Location
            PriceReview=22.22,  # Add a non-null value for Price/Review
            Date=date,
            City=city,
            AsOf=today
        ))
    db_session.commit()

    # Act
    result = get_dates_in_db(db_session, today.strftime('%Y-%m-%d'),
                             (today + timedelta(days=2)).strftime('%Y-%m-%d'), city, as_of=today)

    # Assert
    assert len(result) == 3
    assert set(row.Date for row in result) == set(date.strftime('%Y-%m-%d') for date in dates)


def test_get_dates_in_db_filters_by_city(db_session):
    # Arrange
    today = datetime.now().date()
    city1, city2 = "City1", "City2"
    db_session.add(HotelPrice(
        Hotel="Test Hotel 1",
        Price=100.0,
        Review=4.5,
        Location="Test Location 1",
        PriceReview=22.22,
        Date=today,
        City=city1,
        AsOf=today
    ))
    db_session.add(HotelPrice(
        Hotel="Test Hotel 2",
        Price=150.0,
        Review=4.0,
        Location="Test Location 2",
        PriceReview=37.5,
        Date=today,
        City=city2,
        AsOf=today
    ))
    db_session.commit()

    # Act
    result = get_dates_in_db(db_session, today.strftime('%Y-%m-%d'),
                             today.strftime('%Y-%m-%d'), city1, as_of=today)

    # Assert
    assert len(result) == 1
    assert result[0].Date == today.strftime('%Y-%m-%d')


def test_get_dates_in_db_respects_date_range(db_session):
    # Arrange
    today = datetime.now().date()
    city = "TestCity"
    dates = [today - timedelta(days=1), today, today + timedelta(days=1)]
    for date in dates:
        db_session.add(HotelPrice(
            Hotel=f"Test Hotel {date}",
            Price=100.0,
            Review=4.5,
            Location="Test Location",
            PriceReview=22.22,
            Date=date,
            City=city,
            AsOf=today
        ))
    db_session.commit()

    # Act
    result = get_dates_in_db(db_session, today.strftime('%Y-%m-%d'),
                             today.strftime('%Y-%m-%d'), city, as_of=today)

    # Assert
    assert len(result) == 1
    assert result[0].Date == today.strftime('%Y-%m-%d')


def test_get_dates_in_db_returns_empty_for_no_matches(db_session):
    # Arrange
    today = datetime.now().date()
    city = "TestCity"
    db_session.add(HotelPrice(
        Hotel="Test Hotel",
        Price=100.0,
        Review=4.5,
        Location="Test Location",
        PriceReview=22.22,
        Date=today - timedelta(days=1),
        City=city,
        AsOf=today
    ))
    db_session.commit()

    # Act
    result = get_dates_in_db(db_session, today.strftime('%Y-%m-%d'),
                             (today + timedelta(days=1)).strftime('%Y-%m-%d'), city, as_of=today)

    # Assert
    assert len(result) == 0


def test_get_dates_in_db_returns_correct_dates_with_gaps(db_session):
    # Arrange
    today = datetime.now().date().replace(day=1)  # Start from the first day of the month
    today_as_of = datetime.now().date()
    city = "TestCity"
    dates = [today, today + timedelta(days=2), today + timedelta(days=5)]  # Skip some days
    for date in dates:
        db_session.add(HotelPrice(
            Hotel="Test Hotel",
            Price=100.0,
            Review=4.5,
            Location="Test Location",
            PriceReview=22.22,
            Date=date,
            City=city,
            AsOf=today_as_of
        ))
    db_session.commit()

    # Act
    result = get_dates_in_db(db_session, today.strftime('%Y-%m-%d'),
                             (today + timedelta(days=6)).strftime('%Y-%m-%d'), city, as_of=today_as_of)

    # Assert
    assert len(result) == 3
    assert set(row.Date for row in result) == set(date.strftime('%Y-%m-%d') for date in dates)

    # Check that skipped dates are not in the result
    skipped_dates = [today + timedelta(days=1), today + timedelta(days=3), today + timedelta(days=4)]
    for skipped_date in skipped_dates:
        assert skipped_date.strftime('%Y-%m-%d') not in [row.Date for row in result]