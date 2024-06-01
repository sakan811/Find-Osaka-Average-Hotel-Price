from datetime import datetime

from loguru import logger


def check_if_current_date_has_passed(year, month, day):
    """
    Check if the current date has passed the given day of the month.
    :param year: The year of the date to check.
    :param month: The month of the date to check.
    :param day: The day of the month to check.
    :return: True if the current date has passed the given day, False otherwise.
    """
    today_for_check = datetime.today().strftime('%Y-%m-%d')
    current_date_for_check = datetime(year, month, day).strftime('%Y-%m-%d')
    if current_date_for_check < today_for_check:
        logger.warning(f'The current day of the month to scrape was passed. Skip this day.')
        return True
    else:
        return False
