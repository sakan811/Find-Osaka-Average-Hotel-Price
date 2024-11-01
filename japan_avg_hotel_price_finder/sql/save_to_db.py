import pandas as pd
from sqlalchemy import create_engine, MetaData, func, case, Engine, Float
from sqlalchemy.orm import sessionmaker, Session

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.sql.db_model import Base, HotelPrice, AverageRoomPriceByDate, \
    AverageHotelRoomPriceByReview, AverageHotelRoomPriceByDayOfWeek, AverageHotelRoomPriceByMonth, \
    AverageHotelRoomPriceByLocation


def save_scraped_data(dataframe: pd.DataFrame, engine: Engine) -> None:
    """
    Save scraped data to a database.
    :param dataframe: Pandas DataFrame.
    :param engine: SQLAlchemy engine.
    :return: None
    """
    main_logger.info("Saving scraped data...")
    if not dataframe.empty:
        main_logger.info(f'Save data to a database')
        migrate_data_to_database(dataframe, engine)
    else:
        main_logger.warning('The dataframe is empty. No data to save')


def migrate_data_to_database(df_filtered: pd.DataFrame, engine: Engine) -> None:
    """
    Migrate hotel data to a database using SQLAlchemy ORM.
    :param df_filtered: pandas dataframe.
    :param engine: SQLAlchemy engine.
    :return: None
    """
    main_logger.info('Connecting to a database (or create it if it doesn\'t exist)...')

    # Create all tables
    Base.metadata.create_all(engine)

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
        main_logger.info(f'Data has been saved to a database successfully.')
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

    # Calculate average prices by review, rounding review to nearest integer
    avg_prices = session.query(
        func.round(HotelPrice.Review),
        func.avg(HotelPrice.Price).label('AveragePrice')
    ).group_by(func.round(HotelPrice.Review)).all()

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
        (func.extract('dow', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 0, 'Sunday'),
        (func.extract('dow', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 1, 'Monday'),
        (func.extract('dow', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 2, 'Tuesday'),
        (func.extract('dow', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 3, 'Wednesday'),
        (func.extract('dow', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 4, 'Thursday'),
        (func.extract('dow', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 5, 'Friday'),
        (func.extract('dow', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 6, 'Saturday'),
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
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 1, 'January'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 2, 'February'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 3, 'March'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 4, 'April'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 5, 'May'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 6, 'June'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 7, 'July'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 8, 'August'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 9, 'September'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 10, 'October'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 11, 'November'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')) == 12, 'December'),
    ).label('month')

    # Define the quarter case
    quarter_case = case(
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')).in_([1, 2, 3]), 'Quarter1'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')).in_([4, 5, 6]), 'Quarter2'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')).in_([7, 8, 9]), 'Quarter3'),
        (func.extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD')).in_([10, 11, 12]), 'Quarter4'),
    ).label('quarter')

    # Calculate average prices by month
    avg_prices = session.query(
        month_case,
        func.avg(HotelPrice.Price).label('avg_price'),
        quarter_case
    ).group_by(month_case, quarter_case).all()

    # Create new records
    new_records = [
        AverageHotelRoomPriceByMonth(Month=month, AveragePrice=avg_price, Quarter=quarter)
        for month, avg_price, quarter in avg_prices
    ]

    # Bulk insert new records
    session.bulk_save_objects(new_records)


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