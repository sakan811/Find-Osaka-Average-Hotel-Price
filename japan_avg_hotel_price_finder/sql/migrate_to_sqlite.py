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
        try:
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

            hotel_price_dtype: dict[str, str] = get_hotel_price_dtype()

            # Save the DataFrame to a table named 'HotelPrice'
            df_filtered.to_sql('HotelPrice', con=con, if_exists='append', index=False, dtype=hotel_price_dtype)

            create_avg_hotel_room_price_by_date_table(con)
            create_avg_room_price_by_review_table(con)
            create_avg_hotel_price_by_dow_table(con)
            create_avg_hotel_price_by_month_table(con)
            create_avg_room_price_by_location(con)

            con.commit()
            main_logger.info(f'Data has been saved to {db}')
        except sqlite3.OperationalError as e:
            con.rollback()
            main_logger.error(f"An operational error occurred: {str(e)}")
            main_logger.error("Database changes have been rolled back.")
            raise sqlite3.OperationalError(f"An operational error occurred: {str(e)}")
        except Exception as e:
            con.rollback()
            main_logger.error(f"An unexpected error occurred: {str(e)}")
            main_logger.error("Database changes have been rolled back.")
            raise Exception(f"An unexpected error occurred: {str(e)}")


def get_hotel_price_dtype() -> dict[str, str]:
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


def create_avg_hotel_room_price_by_date_table(connection: sqlite3.Connection) -> None:
    """
    Create AverageHotelRoomPriceByDate table
    :param connection: SQLite database connection
    :return: None
    """
    main_logger.info('Create AverageRoomPriceByDate table...')
    with connection.cursor() as cursor:
        query = '''
        CREATE table IF NOT EXISTS AverageRoomPriceByDateTable (
            Date TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL,
            City TEXT NOT NULL
        ) 
        '''
        cursor.execute(query)

        query = '''
        delete from AverageRoomPriceByDateTable 
        '''
        cursor.execute(query)

        query = '''
        insert into AverageRoomPriceByDateTable (Date, AveragePrice, City)
        select Date, avg(Price) as AveragePrice, City
        from HotelPrice
        GROUP BY Date
        '''
        cursor.execute(query)


def create_avg_room_price_by_review_table(connection: sqlite3.Connection) -> None:
    """
    Create AverageHotelRoomPriceByReview table.
    :param connection: SQLite database connection.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByReview table...")
    with connection.cursor() as cursor:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByReview (
            Review REAL NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL
        ) 
        '''
        cursor.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByReview 
        '''
        cursor.execute(query)

        query = '''
        insert into AverageHotelRoomPriceByReview (Review, AveragePrice)
        select Review, avg(Price)
        FROM HotelPrice
        group by Review
        '''
        cursor.execute(query)


def create_avg_hotel_price_by_dow_table(connection: sqlite3.Connection) -> None:
    """
    Create AverageHotelRoomPriceByDayOfWeek table.
    :param connection: SQLite database connection.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByDayOfWeek table...")
    with connection.cursor() as cursor:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByDayOfWeek (
            DayOfWeek TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL
        ) 
        '''
        cursor.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByDayOfWeek 
        '''
        cursor.execute(query)

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
        cursor.execute(query)


def create_avg_hotel_price_by_month_table(connection: sqlite3.Connection) -> None:
    """
    Create AverageHotelRoomPriceByMonth table.
    :param connection: SQLite database connection.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByMonth table...")
    with connection.cursor() as cursor:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByMonth (
            Month TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL,
            Quarter TEXT NOT NULL
        ) 
        '''
        cursor.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByMonth 
        '''
        cursor.execute(query)

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
        cursor.execute(query)


def create_avg_room_price_by_location(connection: sqlite3.Connection) -> None:
    """
    Create AverageHotelRoomPriceByLocation table.
    :param connection: SQLite database connection.
    :return: None
    """
    main_logger.info("Create AverageHotelRoomPriceByLocation table...")
    with connection.cursor() as cursor:
        query = '''
        CREATE table IF NOT EXISTS AverageHotelRoomPriceByLocation (
            Location TEXT NOT NULL PRIMARY KEY,
            AveragePrice REAL NOT NULL,
            AverageRating REAL NOT NULL,
            AveragePricePerReview REAL NOT NULL
        ) 
        '''
        cursor.execute(query)

        query = '''
        delete from AverageHotelRoomPriceByLocation
        '''
        cursor.execute(query)

        query = '''
        insert into AverageHotelRoomPriceByLocation (Location, AveragePrice, AverageRating, AveragePricePerReview)
        select Location, 
                avg(Price) as AveragePrice, 
                avg(Review) as AverageRating, 
                avg("Price/Review") as AveragePricePerReview
        from HotelPrice
        group by Location;
        '''
        cursor.execute(query)


if __name__ == '__main__':
    pass