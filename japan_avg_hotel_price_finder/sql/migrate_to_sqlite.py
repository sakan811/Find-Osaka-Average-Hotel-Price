import pandas as pd
from sqlalchemy import create_engine, func, case, MetaData
from sqlalchemy.orm import sessionmaker, Session

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.sql.db_model import Base, HotelPrice, AverageRoomPriceByDate, \
    AverageHotelRoomPriceByReview, AverageHotelRoomPriceByDayOfWeek, AverageHotelRoomPriceByMonth, \
    AverageHotelRoomPriceByLocation


def migrate_data_to_sqlite(df_filtered: pd.DataFrame, db: str) -> None:
    """
    Migrate hotel data to sqlite database using SQLAlchemy ORM.
    :param df_filtered: pandas dataframe.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info('Connecting to SQLite database (or create it if it doesn\'t exist)...')

    engine = create_engine(f'sqlite:///{db}')

    # Create a new MetaData instance
    metadata = MetaData()

    # Copy all tables from Base.metadata except JapanHotels
    for table_name, table in Base.metadata.tables.items():
        if table_name != 'JapanHotels':
            table.tometadata(metadata)

    # Create all tables in the new metadata
    metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Rename Price/Review column
        df_filtered.rename(columns={'Price/Review': 'PriceReview'}, inplace=True)

        # Convert DataFrame to list of dictionaries
        records = df_filtered.to_dict('records')

        # Bulk insert records
        session.bulk_insert_mappings(HotelPrice, records)

        create_avg_hotel_room_price_by_date_table(session)
        create_avg_room_price_by_review_table(session)
        create_avg_hotel_price_by_dow_table(session)
        create_avg_hotel_price_by_month_table(session)
        create_avg_room_price_by_location(session)

        session.commit()
        main_logger.info(f'Data has been saved to {db}')
    except Exception as e:
        session.rollback()
        main_logger.error(f"An unexpected error occurred: {str(e)}")
        main_logger.error("Database changes have been rolled back.")
        raise
    finally:
        session.close()


def create_avg_hotel_room_price_by_date_table(session: Session) -> None:
    """
    Create AverageHotelRoomPriceByDate table using SQLAlchemy ORM
    :param session: SQLAlchemy session
    :return: None
    """
    main_logger.info('Create AverageRoomPriceByDate table...')

    # Clear existing data
    session.query(AverageRoomPriceByDate).delete()

    # Insert new data
    avg_prices = session.query(
        HotelPrice.Date,
        func.avg(HotelPrice.Price).label('AveragePrice'),
        HotelPrice.City
    ).group_by(HotelPrice.Date, HotelPrice.City).all()

    new_records = [
        AverageRoomPriceByDate(Date=date, AveragePrice=avg_price, City=city)
        for date, avg_price, city in avg_prices
    ]

    session.bulk_save_objects(new_records)
    session.commit()


def create_avg_room_price_by_review_table(session: Session) -> None:
    """
    Create AverageHotelRoomPriceByReview table using SQLAlchemy ORM.
    :param session: SQLAlchemy session
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByReview table...")

    # Clear existing data
    session.query(AverageHotelRoomPriceByReview).delete()

    # Calculate average prices by review
    avg_prices = session.query(
        HotelPrice.Review,
        func.avg(HotelPrice.Price).label('AveragePrice')
    ).group_by(HotelPrice.Review).all()

    # Create new records
    new_records = [
        AverageHotelRoomPriceByReview(Review=review, AveragePrice=avg_price)
        for review, avg_price in avg_prices
    ]

    # Bulk insert new records
    session.bulk_save_objects(new_records)
    session.commit()


def create_avg_hotel_price_by_dow_table(session: Session) -> None:
    """
    Create AverageHotelRoomPriceByDayOfWeek table using SQLAlchemy ORM.
    :param session: SQLAlchemy session
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByDayOfWeek table...")

    # Clear existing data
    session.query(AverageHotelRoomPriceByDayOfWeek).delete()

    # Calculate average prices by day of week
    day_of_week_case = case(
        (func.strftime('%w', HotelPrice.Date) == '0', 'Sunday'),
        (func.strftime('%w', HotelPrice.Date) == '1', 'Monday'),
        (func.strftime('%w', HotelPrice.Date) == '2', 'Tuesday'),
        (func.strftime('%w', HotelPrice.Date) == '3', 'Wednesday'),
        (func.strftime('%w', HotelPrice.Date) == '4', 'Thursday'),
        (func.strftime('%w', HotelPrice.Date) == '5', 'Friday'),
        (func.strftime('%w', HotelPrice.Date) == '6', 'Saturday'),
    ).label('day_of_week')

    avg_prices = session.query(
        day_of_week_case,
        func.avg(HotelPrice.Price).label('avg_price')
    ).group_by(day_of_week_case).all()

    # Create new records
    new_records = [
        AverageHotelRoomPriceByDayOfWeek(DayOfWeek=day_of_week, AveragePrice=avg_price)
        for day_of_week, avg_price in avg_prices
    ]

    # Bulk insert new records
    session.bulk_save_objects(new_records)
    session.commit()


def create_avg_hotel_price_by_month_table(session: Session) -> None:
    """
    Create AverageHotelRoomPriceByMonth table using SQLAlchemy ORM.
    :param session: SQLAlchemy session
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByMonth table...")

    # Clear existing data
    session.query(AverageHotelRoomPriceByMonth).delete()

    # Define the month case
    month_case = case(
        (func.strftime('%m', HotelPrice.Date) == '01', 'January'),
        (func.strftime('%m', HotelPrice.Date) == '02', 'February'),
        (func.strftime('%m', HotelPrice.Date) == '03', 'March'),
        (func.strftime('%m', HotelPrice.Date) == '04', 'April'),
        (func.strftime('%m', HotelPrice.Date) == '05', 'May'),
        (func.strftime('%m', HotelPrice.Date) == '06', 'June'),
        (func.strftime('%m', HotelPrice.Date) == '07', 'July'),
        (func.strftime('%m', HotelPrice.Date) == '08', 'August'),
        (func.strftime('%m', HotelPrice.Date) == '09', 'September'),
        (func.strftime('%m', HotelPrice.Date) == '10', 'October'),
        (func.strftime('%m', HotelPrice.Date) == '11', 'November'),
        (func.strftime('%m', HotelPrice.Date) == '12', 'December'),
    ).label('month')

    # Define the quarter case
    quarter_case = case(
        (func.strftime('%m', HotelPrice.Date).in_(['01', '02', '03']), 'Quarter1'),
        (func.strftime('%m', HotelPrice.Date).in_(['04', '05', '06']), 'Quarter2'),
        (func.strftime('%m', HotelPrice.Date).in_(['07', '08', '09']), 'Quarter3'),
        (func.strftime('%m', HotelPrice.Date).in_(['10', '11', '12']), 'Quarter4'),
    ).label('quarter')

    # Calculate average prices by month
    avg_prices = session.query(
        month_case,
        func.avg(HotelPrice.Price).label('avg_price'),
        quarter_case
    ).group_by(month_case).all()

    # Create new records
    new_records = [
        AverageHotelRoomPriceByMonth(Month=month, AveragePrice=avg_price, Quarter=quarter)
        for month, avg_price, quarter in avg_prices
    ]

    # Bulk insert new records
    session.bulk_save_objects(new_records)
    session.commit()


def create_avg_room_price_by_location(session: Session) -> None:
    """
    Create AverageHotelRoomPriceByLocation table using SQLAlchemy ORM.
    :param session: SQLAlchemy session
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByLocation table...")

    # Clear existing data
    session.query(AverageHotelRoomPriceByLocation).delete()

    # Calculate average prices, ratings, and price per review by location
    avg_data = session.query(
        HotelPrice.Location,
        func.avg(HotelPrice.Price).label('AveragePrice'),
        func.avg(HotelPrice.Review).label('AverageRating'),
        func.avg(HotelPrice.PriceReview).label('AveragePricePerReview')
    ).group_by(HotelPrice.Location).all()

    # Create new records
    new_records = [
        AverageHotelRoomPriceByLocation(
            Location=location,
            AveragePrice=avg_price,
            AverageRating=avg_rating,
            AveragePricePerReview=avg_price_per_review
        )
        for location, avg_price, avg_rating, avg_price_per_review in avg_data
    ]

    # Bulk insert new records
    session.bulk_save_objects(new_records)
    session.commit()


if __name__ == '__main__':
    pass
