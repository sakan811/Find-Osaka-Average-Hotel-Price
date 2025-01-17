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


def add_japan_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add Japan-related arguments to the parser.
    :param parser: argparse.ArgumentParser
    :return: None
    """
    parser.add_argument('--prefecture', type=str, nargs='+', help='Prefecture(s) to scrape data for')
    parser.add_argument('--start_month', type=int, default=1, 
                       help='Month to start scraping (1-12), default is 1')
    parser.add_argument('--end_month', type=int, default=12,
                       help='Last month to scrape (1-12), default is 12')


def validate_japan_arguments(args: argparse.Namespace) -> None:
    """
    Validate Japan-specific arguments.
    :param args: Argparse.Namespace
    :return: None
    """
    if args.prefecture and not args.japan_hotel:
        main_logger.error(
            "Error: The --prefecture argument can only be used with the Japan hotel scraper (--japan_hotel).")
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
    add_date_arguments(parser)
    add_japan_arguments(parser)
    args = parser.parse_args()
    validate_booking_details_arguments(args)
    validate_japan_arguments(args)
    return args
