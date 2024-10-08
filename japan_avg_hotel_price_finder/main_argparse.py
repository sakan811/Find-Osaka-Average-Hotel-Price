import argparse

from japan_avg_hotel_price_finder.configure_logging import main_logger


def add_scraper_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add scraper-related arguments to the parser.
    :param parser: argparse.ArgumentParser
    :return: None
    """
    scraper_group = parser.add_mutually_exclusive_group(required=True)
    scraper_group.add_argument('--scraper', action='store_true', help='Use basic GraphQL scraper')
    scraper_group.add_argument('--whole_mth', action='store_true', help='Use Whole-Month GraphQL scraper')
    scraper_group.add_argument('--japan_hotel', action='store_true', help='Use Japan Hotel GraphQL scraper')


def add_booking_details_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add booking details arguments to the parser.
    :param parser: argparse.ArgumentParser
    :return: None
    """
    parser.add_argument('--city', type=str, help='City where the hotels are located')
    parser.add_argument('--country', type=str, help='Country where the hotels are located', default='Japan')
    parser.add_argument('--check_in', type=str, help='Check-in date')
    parser.add_argument('--check_out', type=str, help='Check-out date')
    parser.add_argument('--group_adults', type=int, default=1, help='Number of Adults, default is 1')
    parser.add_argument('--num_rooms', type=int, default=1, help='Number of Rooms, default is 1')
    parser.add_argument('--group_children', type=int, default=0, help='Number of Children, default is 0')
    parser.add_argument('--selected_currency', type=str, default='USD', help='Room price currency, default is "USD"')
    parser.add_argument('--scrape_only_hotel', action='store_true', help='Whether to scrape only hotel properties')


def add_database_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add database-related arguments to the parser.
    :param parser: argparse.ArgumentParser
    :return: None
    """
    db_group = parser.add_mutually_exclusive_group(required=True)
    db_group.add_argument('--sqlite_name', type=str, help='SQLite database path')
    db_group.add_argument('--duckdb_name', type=str, help='DuckDB database path')


def add_date_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add date and length of stay arguments to the parser.
    :param parser: argparse.ArgumentParser
    :return: None
    """
    parser.add_argument('--year', type=int, help='Year to scrape')
    parser.add_argument('--month', type=int, help='Month to scrape')
    parser.add_argument('--start_day', type=int, default=1,
                        help='The day of the month to start scraping from, default is 1')
    parser.add_argument('--nights', type=int, default=1, help='Length of stay, default is 1')


def enforce_database_constraints(args: argparse.Namespace) -> None:
    """
    Enforce the use of SQLite for basic and whole-month scrapers, and DuckDB for Japan scraper.
    :param args: argparse.Namespace
    :return: None
    """
    if args.scraper or args.whole_mth:
        if args.duckdb_name:
            main_logger.error("Error: DuckDB should not be used with the basic or whole-month scraper.")
            raise SystemExit
        if not args.sqlite_name:
            main_logger.error("Error: SQLite database path must be provided for the basic or whole-month scraper.")
            raise SystemExit

    if args.japan_hotel:
        if args.sqlite_name:
            main_logger.error("Error: SQLite should not be used with the Japan hotel scraper.")
            raise SystemExit
        if not args.duckdb_name:
            main_logger.error("Error: DuckDB database path must be provided for the Japan hotel scraper.")
            raise SystemExit


def validate_booking_details_arguments(args: argparse.Namespace) -> None:
    """
    Validate the parsed arguments of booking details.
    :param args: Argparse.Namespace
    :return: None
    """
    if args.group_adults <= 0:
        main_logger.error("Error: The number of adults must be greater than 0.")
        raise SystemExit
    if args.num_rooms <= 0:
        main_logger.error("Error: The number of rooms must be greater than 0.")
        raise SystemExit
    if args.group_children < 0:
        main_logger.error("Error: The number of children must be greater than or equal to 0.")
        raise SystemExit


def parse_arguments() -> argparse.Namespace:
    """
    Parse the command line arguments.
    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='Parser that controls which kind of scraper to use.')
    add_scraper_arguments(parser)
    add_booking_details_arguments(parser)
    add_database_arguments(parser)
    add_date_arguments(parser)
    args = parser.parse_args()
    enforce_database_constraints(args)
    validate_booking_details_arguments(args)
    return args
