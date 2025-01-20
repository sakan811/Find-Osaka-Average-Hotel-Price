import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from japan_avg_hotel_price_finder.sql.db_model import Base, HotelPrice, AverageHotelRoomPriceByLocation
from japan_avg_hotel_price_finder.sql.save_to_db import create_avg_room_price_by_location


@pytest.fixture
def today():
    return datetime.datetime.now().date()


@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    session.close()


def test_create_avg_room_price_by_location_sqlite(db_session, today):
    # Given
    test_data = [
        # Location 1 data
        HotelPrice(Hotel="Hotel A1", Price=100, Review=4.5, Location="Location1", PriceReview=22.2, City="Tokyo", 
                   Date=today, AsOf=today),
        HotelPrice(Hotel="Hotel A2", Price=200, Review=4.0, Location="Location1", PriceReview=50.0, City="Tokyo",
                   Date=today, AsOf=today),
        HotelPrice(Hotel="Hotel A3", Price=150, Review=4.2, Location="Location1", PriceReview=35.7, City="Tokyo",
                   Date=today, AsOf=today),
        # Location 2 data
        HotelPrice(Hotel="Hotel B1", Price=300, Review=4.8, Location="Location2", PriceReview=62.5, City="Osaka",
                   Date=today, AsOf=today),
        HotelPrice(Hotel="Hotel B2", Price=250, Review=4.6, Location="Location2", PriceReview=54.3, City="Osaka",
                   Date=today, AsOf=today),
    ]
    for hotel in test_data:
        db_session.add(hotel)
    db_session.commit()

    # When
    create_avg_room_price_by_location(db_session)

    # Then
    results = db_session.query(AverageHotelRoomPriceByLocation).order_by(AverageHotelRoomPriceByLocation.Location).all()
    
    assert len(results) == 2

    # Check Location1 medians
    location1 = results[0]
    assert location1.Location == "Location1"
    assert abs(location1.AveragePrice - 150) < 0.1  # Median of [100, 150, 200]
    assert abs(location1.AverageRating - 4.2) < 0.1  # Median of [4.0, 4.2, 4.5]
    assert abs(location1.AveragePricePerReview - 35.7) < 0.1  # Median of [22.2, 35.7, 50.0]

    # Check Location2 medians
    location2 = results[1]
    assert location2.Location == "Location2"
    assert abs(location2.AveragePrice - 275) < 0.1  # Median of [250, 300]
    assert abs(location2.AverageRating - 4.7) < 0.1  # Median of [4.6, 4.8]
    assert abs(location2.AveragePricePerReview - 58.4) < 0.1  # Median of [54.3, 62.5]


def test_create_avg_room_price_by_location_empty(db_session):
    # When
    create_avg_room_price_by_location(db_session)

    # Then
    results = db_session.query(AverageHotelRoomPriceByLocation).all()
    assert len(results) == 0


def test_create_avg_room_price_by_location_single_entry(db_session, today):
    # Given
    hotel = HotelPrice(
        Hotel="Hotel A",
        Price=100,
        Review=4.5,
        Location="Location1",
        PriceReview=22.2,
        City="Tokyo",
        Date=today,
        AsOf=today
    )
    db_session.add(hotel)
    db_session.commit()

    # When
    create_avg_room_price_by_location(db_session)

    # Then
    result = db_session.query(AverageHotelRoomPriceByLocation).first()
    assert result.Location == "Location1"
    assert abs(result.AveragePrice - 100) < 0.1
    assert abs(result.AverageRating - 4.5) < 0.1
    assert abs(result.AveragePricePerReview - 22.2) < 0.1


def test_create_avg_room_price_by_location_clears_existing(db_session, today):
    # Given
    # Add initial data
    hotel1 = HotelPrice(
        Hotel="Hotel A",
        Price=100,
        Review=4.5,
        Location="Location1",
        PriceReview=22.2,
        City="Tokyo",
        Date=today,
        AsOf=today
    )
    db_session.add(hotel1)
    db_session.commit()
    
    create_avg_room_price_by_location(db_session)
    initial_count = db_session.query(AverageHotelRoomPriceByLocation).count()
    assert initial_count == 1

    # Add more data
    hotel2 = HotelPrice(
        Hotel="Hotel B",
        Price=200,
        Review=4.0,
        Location="Location2",
        PriceReview=50.0,
        City="Osaka",
        Date=today,
        AsOf=today
    )
    db_session.add(hotel2)
    db_session.commit()

    # When
    create_avg_room_price_by_location(db_session)

    # Then
    results = db_session.query(AverageHotelRoomPriceByLocation).order_by(AverageHotelRoomPriceByLocation.Location).all()
    assert len(results) == 2
    assert results[0].Location == "Location1"
    assert results[1].Location == "Location2" 