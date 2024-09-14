import argparse
import asyncio

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.japan_hotel_scraper import JapanScraper
from japan_avg_hotel_price_finder.utils import save_scraped_data
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper


def parse_arguments() -> argparse.Namespace:
    """
    Parse the command line arguments
    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='Parser that controls which kind of scraper to use.')

    # Mutually exclusive scrapers
    scraper_group = parser.add_mutually_exclusive_group(required=True)
    scraper_group.add_argument('--scraper', action='store_true', help='Use basic GraphQL scraper')
    scraper_group.add_argument('--whole_mth', action='store_true', help='Use Whole-Month GraphQL scraper')
    scraper_group.add_argument('--japan_hotel', action='store_true', help='Use Japan Hotel GraphQL scraper')

    # Booking details arguments
    parser.add_argument('--city', type=str, help='City where the hotels are located')
    parser.add_argument('--country', type=str, help='Country where the hotels are located',
                        default='Japan')
    parser.add_argument('--check_in', type=str, help='Check-in date')
    parser.add_argument('--check_out', type=str, help='Check-out date')
    parser.add_argument('--group_adults', type=int, default=1, help='Number of Adults, default is 1')
    parser.add_argument('--num_rooms', type=int, default=1, help='Number of Rooms, default is 1')
    parser.add_argument('--group_children', type=int, default=0, help='Number of Children, default is 0')
    parser.add_argument('--selected_currency', type=str, default='USD',
                        help='Room price currency, default is "USD"')
    parser.add_argument('--scrape_only_hotel', action='store_true',
                        help='Whether to scrape only hotel properties')

    # Database paths
    parser.add_argument('--sqlite_name', type=str, default='avg_japan_hotel_price_test.db',
                        help='SQLite database path, default is "avg_japan_hotel_price_test.db"')
    parser.add_argument('--duckdb_name', type=str, default='japan_hotel_data_test.duckdb',
                        help='DuckDB database path, default is "japan_hotel_data_test.duckdb"')

    # Date and Length of Stay arguments
    parser.add_argument('--year', type=int, help='Year to scrape')
    parser.add_argument('--month', type=int, help='Month to scrape')
    parser.add_argument('--start_day', type=int, default=1,
                        help='The day of the month to start scraping from, default is 1')
    parser.add_argument('--nights', type=int, default=1, help='Length of stay, default is 1')

    args = parser.parse_args()

    # Logic to enforce SQLite for basic and whole-month scrapers, and DuckDB for Japan scraper
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

    return args


def validate_required_args(arguments: argparse.Namespace, required_args: list[str]) -> bool:
    """
    Validate the required arguments
    :param arguments: Arguments to validate
    :param required_args: List of required arguments
    :return: bool
    """
    missing_args = [arg for arg in required_args if not getattr(arguments, arg)]
    if missing_args:
        main_logger.warning(f"Please provide the following required arguments: {', '.join(missing_args)}")
        return False
    return True


def run_whole_month_scraper(arguments: argparse.Namespace) -> None:
    """
    Run the Whole-Month GraphQL scraper
    :param arguments: Arguments to pass to the scraper
    :return: None
    """
    required_args = ['year', 'month', 'city', 'country']
    if validate_required_args(arguments, required_args):
        scraper = WholeMonthGraphQLScraper(
            city=arguments.city, year=arguments.year, month=arguments.month, start_day=arguments.start_day,
            nights=arguments.nights, scrape_only_hotel=arguments.scrape_only_hotel, sqlite_name=arguments.sqlite_name,
            selected_currency=arguments.selected_currency, group_adults=arguments.group_adults,
            num_rooms=arguments.num_rooms, group_children=arguments.group_children, check_in='', check_out='',
            country=arguments.country
        )
        df = asyncio.run(scraper.scrape_whole_month())
        save_scraped_data(dataframe=df, db=scraper.sqlite_name)


def run_japan_hotel_scraper(arguments: argparse.Namespace) -> None:
    """
    Run the Japan hotel scraper
    :param arguments: Arguments to pass to the scraper
    :return: None
    """
    year: int = 2024
    month: int = 1
    scraper = JapanScraper(
        city='', year=year, month=month, start_day=arguments.start_day, nights=arguments.nights,
        scrape_only_hotel=arguments.scrape_only_hotel, sqlite_name='', selected_currency=arguments.selected_currency,
        group_adults=arguments.group_adults, num_rooms=arguments.num_rooms, group_children=arguments.group_children,
        check_in='', check_out='', duckdb_path=arguments.duckdb_name, country=arguments.country
    )
    asyncio.run(scraper.scrape_japan_hotels())


def run_basic_scraper(arguments: argparse.Namespace) -> None:
    """
    Run the Basic GraphQL scraper
    :param arguments: Arguments to pass to the scraper
    :return: None
    """
    required_args = ['check_in', 'check_out', 'city', 'country']
    if validate_required_args(arguments, required_args):
        scraper = BasicGraphQLScraper(
            city=arguments.city, scrape_only_hotel=arguments.scrape_only_hotel, sqlite_name=arguments.sqlite_name,
            selected_currency=arguments.selected_currency, group_adults=arguments.group_adults,
            num_rooms=arguments.num_rooms, group_children=arguments.group_children, check_in=arguments.check_in,
            check_out=arguments.check_out, country=arguments.country
        )
        df = asyncio.run(scraper.scrape_graphql())
        save_scraped_data(dataframe=df, db=scraper.sqlite_name)


def main() -> None:
    """
    Main function to run the scraper
    :return: None
    """
    arguments = parse_arguments()
    if arguments.whole_mth:
        run_whole_month_scraper(arguments)
    elif arguments.japan_hotel:
        run_japan_hotel_scraper(arguments)
    else:
        run_basic_scraper(arguments)


if __name__ == '__main__':
    main()
