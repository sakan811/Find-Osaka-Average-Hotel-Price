from collections import defaultdict

import numpy as np
import pandas as pd
from sqlalchemy import func, case, Engine, extract, Integer, cast
from sqlalchemy.dialects import sqlite, postgresql
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
    Create AverageHotelRoomPriceByDate table using the median (instead of average).
    Supports PostgreSQL and SQLite.
    :param session: SQLAlchemy session
    :return: None
    """
    main_logger.info('Create AverageRoomPriceByDate table...')

    # Clear existing data
    session.query(AverageRoomPriceByDate).delete()

    # Detect database dialect
    dialect = session.bind.dialect

    if isinstance(dialect, postgresql.dialect):
        # PostgreSQL specific median calculation using `percentile_cont`
        median_subquery = session.query(
            HotelPrice.Date,
            HotelPrice.City,
            func.percentile_cont(0.5).within_group(HotelPrice.Price).label('MedianPrice')
        ).group_by(HotelPrice.Date, HotelPrice.City).subquery()

        median_data = session.query(
            median_subquery.c.Date,
            median_subquery.c.MedianPrice,
            median_subquery.c.City
        ).all()

    elif isinstance(dialect, sqlite.dialect):
        # SQLite: Calculate median in Python by fetching grouped data
        grouped_data = session.query(
            HotelPrice.Date,
            HotelPrice.City,
            HotelPrice.Price
        ).order_by(HotelPrice.Date, HotelPrice.City, HotelPrice.Price).all()

        # Organize data into groups by (Date, City)
        from collections import defaultdict
        grouped_prices = defaultdict(list)
        for date, city, price in grouped_data:
            grouped_prices[(date, city)].append(price)

        # Calculate median for each group
        median_data = [
            (date, np.median(prices), city)
            for (date, city), prices in grouped_prices.items()
        ]

    else:
        raise NotImplementedError("Median calculation is only implemented for PostgreSQL and SQLite.")

    # Create new records
    new_records = [
        AverageRoomPriceByDate(Date=date, AveragePrice=median_price, City=city)
        for date, median_price, city in median_data
    ]

    # Bulk insert new records
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

    # Detect database dialect
    dialect = session.bind.dialect

    if isinstance(dialect, postgresql.dialect):
        # PostgreSQL specific date extraction
        dow_func = extract('dow', func.to_date(HotelPrice.Date, 'YYYY-MM-DD'))
    elif isinstance(dialect, sqlite.dialect):
        # SQLite specific date extraction
        dow_func = func.cast(func.strftime('%w', func.date(HotelPrice.Date)), Integer)
    else:
        raise NotImplementedError(f"Unsupported dialect: {dialect}")

    # Calculate average prices by day of week
    day_of_week_case = case(
        (dow_func == 0, 'Sunday'),
        (dow_func == 1, 'Monday'),
        (dow_func == 2, 'Tuesday'),
        (dow_func == 3, 'Wednesday'),
        (dow_func == 4, 'Thursday'),
        (dow_func == 5, 'Friday'),
        (dow_func == 6, 'Saturday'),
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
    Create AverageHotelRoomPriceByMonth table using the median instead of average.
    Supports PostgreSQL and SQLite.
    :param session: SQLAlchemy session
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByMonth table...")

    # Clear existing data
    session.query(AverageHotelRoomPriceByMonth).delete()

    # Detect database dialect
    dialect = session.bind.dialect

    if isinstance(dialect, postgresql.dialect):
        # PostgreSQL-specific date extraction
        month_func = extract('month', func.to_date(HotelPrice.Date, 'YYYY-MM-DD'))
        quarter_case = case(
            (month_func.in_([1, 2, 3]), 'Quarter1'),
            (month_func.in_([4, 5, 6]), 'Quarter2'),
            (month_func.in_([7, 8, 9]), 'Quarter3'),
            (month_func.in_([10, 11, 12]), 'Quarter4'),
        ).label('quarter')

        # Query grouped by Month and Quarter with median calculation
        median_subquery = session.query(
            month_func.label('Month'),
            quarter_case.label('Quarter'),
            func.percentile_cont(0.5).within_group(HotelPrice.Price).label('MedianPrice')
        ).group_by(month_func, quarter_case).subquery()

        median_data = session.query(
            median_subquery.c.Month,
            median_subquery.c.MedianPrice,
            median_subquery.c.Quarter
        ).all()

    elif isinstance(dialect, sqlite.dialect):
        # SQLite-specific date extraction
        month_func = cast(func.strftime('%m', HotelPrice.Date), Integer)

        # Gather data for Python-based median calculation
        grouped_data = session.query(
            month_func.label('Month'),
            HotelPrice.Price  # Include only the necessary columns
        ).all()

        # Organize it by Month
        price_by_month = defaultdict(list)
        for month, price in grouped_data:
            price_by_month[month].append(price)

        # Calculate the median price for each month
        median_data = []
        for month, prices in price_by_month.items():
            median_price = np.median(prices)
            quarter = 'Quarter1' if month in [1, 2, 3] else \
                'Quarter2' if month in [4, 5, 6] else \
                    'Quarter3' if month in [7, 8, 9] else \
                        'Quarter4'
            median_data.append((month, median_price, quarter))

    else:
        raise NotImplementedError(f"Unsupported dialect: {dialect}")

    # Map numeric months to readable names
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }

    # Create new records
    new_records = [
        AverageHotelRoomPriceByMonth(Month=month_names[month], AveragePrice=median_price, Quarter=quarter)
        for month, median_price, quarter in median_data
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
