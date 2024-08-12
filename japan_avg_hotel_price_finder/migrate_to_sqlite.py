import sqlite3

import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import main_logger


def migrate_data_to_sqlite(df_filtered: pd.DataFrame, db: str) -> None:
    """
    Migrate hotel data to sqlite database.
    :param df_filtered: pandas dataframe.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info('Connecting to SQLite database (or create it if it doesn\'t exist)...')

    with sqlite3.connect(db) as con:
        query = '''
        CREATE TABLE IF NOT EXISTS HotelPrice (
            ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Hotel TEXT NOT NULL,
            Price REAL NOT NULL,
            Review REAL NOT NULL,
            Location TEXT NOT NULL,
            "Price/Review" REAL NOT NULL,
            City TEXT NOT NULL,
            Date TEXT NOT NULL,
            AsOf TEXT NOT NULL
        )
        '''

        con.execute(query)

        hotel_price_dtype: dict = get_hotel_price_dtype()

        # Save the DataFrame to a table named 'HotelPrice'
        df_filtered.to_sql('HotelPrice', con=con, if_exists='append', index=False, dtype=hotel_price_dtype)

        con.commit()

        main_logger.info(f'Data has been saved to {db}')

        create_average_room_price_by_date_view(db)

        create_avg_hotel_room_price_by_date_table(db)

        create_avg_room_price_by_review_table(db)

        create_avg_hotel_price_by_dow_table(db)

        create_avg_hotel_price_by_month_table(db)

        create_avg_room_price_by_location(db)


def get_hotel_price_dtype() -> dict:
    """
    Get HotelPrice datatype.
    :return: HotelPrice datatype.
    """
    main_logger.info('Get HotelPrice datatype...')
    hotel_price_dtype = {
        'Hotel': 'text not null primary key',
        'Price': 'real not null',
        'Review': 'real not null',
        'Location': 'text not null',
        'Price/Review': 'real not null',
        'City': 'text not null',
        'Date': 'text not null',
        'AsOf': 'text not null'
    }
    return hotel_price_dtype


def create_average_room_price_by_date_view(db: str) -> None:
    """
    Create AverageRoomPriceByDate view
    :param db: SQLite database path
    :return: None
    """
    main_logger.info('Create AverageRoomPriceByDate view...')
    with sqlite3.connect(db) as con:
        query = '''
        CREATE VIEW IF NOT EXISTS AverageRoomPriceByDate AS 
        select Date, avg(Price) as AveragePrice, City
        from HotelPrice
        GROUP BY Date
        '''
        con.execute(query)


def create_avg_hotel_room_price_by_date_table(db: str) -> None:
    """
    Create AverageHotelRoomPriceByDate table
    :param db: SQLite database path
    :return: None
    """
    main_logger.info('Create AverageRoomPriceByDate table...')
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageRoomPriceByDateTable (
            Date TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL,
            City TEXT NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageRoomPriceByDateTable 
        '''
        con.execute(query)

        query = '''
        insert into AverageRoomPriceByDateTable (Date, AveragePrice, City)
        select Date, avg(Price) as AveragePrice, City
        from HotelPrice
        GROUP BY Date
        '''
        con.execute(query)


def create_avg_room_price_by_review_table(db: str) -> None:
    """
    Create AverageHotelRoomPriceByReview table.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByReview table...")
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByReview (
            Review REAL NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByReview 
        '''
        con.execute(query)

        query = '''
        insert into AverageHotelRoomPriceByReview (Review, AveragePrice)
        select Review, avg(Price)
        FROM HotelPrice
        group by Review
        '''
        con.execute(query)


def create_avg_hotel_price_by_dow_table(db: str) -> None:
    """
    Create AverageHotelRoomPriceByDayOfWeek table.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByDayOfWeek table...")
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByDayOfWeek (
            DayOfWeek TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByDayOfWeek 
        '''
        con.execute(query)

        query = '''
        insert into AverageHotelRoomPriceByDayOfWeek (DayOfWeek, AveragePrice)
        SELECT
            CASE strftime('%w', Date)
                WHEN '0' THEN 'Sunday'
                WHEN '1' THEN 'Monday'
                WHEN '2' THEN 'Tuesday'
                WHEN '3' THEN 'Wednesday'
                WHEN '4' THEN 'Thursday'
                WHEN '5' THEN 'Friday'
                WHEN '6' THEN 'Saturday'
            END AS day_of_week,
            AVG(Price) AS avg_price
        FROM
            HotelPrice
        GROUP BY
            day_of_week;
        '''
        con.execute(query)


def create_avg_hotel_price_by_month_table(db: str) -> None:
    """
    Create AverageHotelRoomPriceByMonth table.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByMonth table...")
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByMonth (
            Month TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL,
            Quarter TEXT NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByMonth 
        '''
        con.execute(query)

        query = '''
        insert into AverageHotelRoomPriceByMonth (Month, AveragePrice, Quarter)
        SELECT
            CASE strftime('%m', Date)
                WHEN '01' THEN 'January'
                WHEN '02' THEN 'February'
                WHEN '03' THEN 'March'
                WHEN '04' THEN 'April'
                WHEN '05' THEN 'May'
                WHEN '06' THEN 'June'
                WHEN '07' THEN 'July'
                WHEN '08' THEN 'August'
                WHEN '09' THEN 'September'
                WHEN '10' THEN 'October'
                WHEN '11' THEN 'November'
                WHEN '12' THEN 'December'
            END AS month,
            AVG(Price) AS avg_price,
            CASE
                WHEN strftime('%m', Date) IN ('01', '02', '03') THEN 'Quarter1'
                WHEN strftime('%m', Date) IN ('04', '05', '06') THEN 'Quarter2'
                WHEN strftime('%m', Date) IN ('07', '08', '09') THEN 'Quarter3'
                WHEN strftime('%m', Date) IN ('10', '11', '12') THEN 'Quarter4'
            END AS quarter
        FROM
            HotelPrice
        GROUP BY
            month;
        '''
        con.execute(query)


def create_avg_room_price_by_location(db: str) -> None:
    """
    Create AverageHotelRoomPriceByLocation table.
    :param db: SQLite database path.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByLocation table...")
    with sqlite3.connect(db) as con:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByLocation (
            Location TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL,
            City TEXT NOT NULL,
            HotelCount REAL NOT NULL
        ) 
        '''
        con.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByLocation
        '''
        con.execute(query)

        query = '''
        insert into AverageHotelRoomPriceByLocation (Location, AveragePrice, City, HotelCount)
        select Location, avg(Price), City, count(Location)
        FROM HotelPrice
        group by Location;
        '''
        con.execute(query)


if __name__ == '__main__':
    pass
