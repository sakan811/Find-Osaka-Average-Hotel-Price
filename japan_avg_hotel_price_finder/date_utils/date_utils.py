import datetime

from japan_avg_hotel_price_finder.configure_logging import main_logger


def check_if_current_date_has_passed(year: int, month: int, day: int, timezone=None) -> bool:
    """
    Check if the current date has passed the given day of the month.
    :param year: The year of the date to check.
    :param month: The month of the date to check.
    :param day: The day of the month to check.
    :param timezone: Set timezone.
                    Default is None.
    :return: True if the current date has passed the given day, False otherwise.
    """
    if timezone is not None:
        today = datetime.datetime.now(timezone)
    else:
        today = datetime.datetime.today()

    today_date = today.date()

    try:
        entered_date = datetime.date(year, month, day)
        if entered_date < today_date:
            return True
        else:
            return False
    except ValueError:
        main_logger.error("Invalid date. Returning False")
        return False


def format_date(date_obj: datetime.date) -> str:
    """
    Formats a date object to 'YYYY-MM-DD' string format.

    :param date_obj: The date object to format
    :return: Formatted date string
    """
    try:
        date_str = date_obj.strftime('%Y-%m-%d')
        # Ensure the year is always 4 digits
        year, month, day = date_str.split('-')
        return f"{int(year):04d}-{month}-{day}"
    except AttributeError as e:
        main_logger.error(f"Invalid date: {date_obj}. {str(e)}")
        raise AttributeError(f'Invalid date: {date_obj}. {str(e)}')
    except Exception as e:
        main_logger.error(f"Unexpected error: {str(e)}")
        raise Exception(f'Unexpected error: {str(e)}')