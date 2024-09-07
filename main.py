import argparse
import asyncio

from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.utils import save_scraped_data
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper
from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.japan_hotel_scraper import JapanScraper

# Initialize argument parser
parser = argparse.ArgumentParser(description='Parser that control which kind of scraper to use.')
parser.add_argument('--scraper', type=bool, default=True, help='Use basic GraphQL scraper')
parser.add_argument('--whole_mth', type=bool, default=False, help='Use Whole-Month GraphQL scraper')
parser.add_argument('--japan_hotel', type=bool, default=False, help='Use Japan Hotel GraphQL scraper')
parser.add_argument('--city', type=str, help='City where the hotels are located')
parser.add_argument('--country', type=str, help='Country where the hotels are located', default='Japan')
parser.add_argument('--check_in', type=str, help='Check-in date')
parser.add_argument('--check_out', type=str, help='Check-out date')
parser.add_argument('--group_adults', type=int, default=1, help='Number of Adults, default is 1')
parser.add_argument('--num_rooms', type=int, default=1, help='Number of Rooms, default is 1')
parser.add_argument('--group_children', type=int, default=0, help='Number of Children, default is 0')
parser.add_argument('--selected_currency', type=str, default='USD', help='Room price currency, default is "USD"')
parser.add_argument('--scrape_only_hotel', type=bool, default=True, help='Whether to scrape only hotel properties, '
                                                                         'default is True')
parser.add_argument('--sqlite_name', type=str, default='avg_japan_hotel_price_test.db',
                    help='SQLite database path, default is "avg_japan_hotel_price_test.db"')
parser.add_argument('--duckdb_name', type=str, default='japan_hotel_data_test.duckdb',
                    help='DuckDB database path, default is "japan_hotel_data_test.duckdb"')
parser.add_argument('--year', type=int, help='Year to scrape')
parser.add_argument('--month', type=int, help='Month to scrape')
parser.add_argument('--start_day', type=int, default=1,
                    help='The day of the month to start scraping from, default is 1')
parser.add_argument('--nights', type=int, default=1, help='Length of stay, default is 1')
args = parser.parse_args()


def validate_required_args(required_args: list[argparse.Namespace], arg_names: list[str]) -> bool:
    missing_args: list[str] = [arg_name for arg, arg_name in zip(required_args, arg_names) if not arg]
    if missing_args:
        main_logger.warning(f"Please provide the following required arguments: {', '.join(missing_args)}")
        return False
    return True


def main(arguments: argparse.Namespace) -> None:
    # Set default parameters
    country: str = arguments.country
    nights: int = arguments.nights
    scrape_only_hotel: bool = arguments.scrape_only_hotel
    selected_currency: str = arguments.selected_currency
    start_day: int = arguments.start_day
    group_adults: int = arguments.group_adults
    num_rooms: int = arguments.num_rooms
    group_children: int = arguments.group_children
    sqlite_name: str = arguments.sqlite_name
    duckdb_name: str = arguments.duckdb_name

    if arguments.whole_mth:
        required_args = [arguments.year, arguments.month, arguments.city, arguments.country]
        if validate_required_args(required_args, ['--year', '--month', '--city', '--country']):
            year: int = arguments.year
            month: int = arguments.month
            city: str = arguments.city

            scraper = WholeMonthGraphQLScraper(city=city, year=year, month=month, start_day=start_day,
                                               nights=nights,
                                               scrape_only_hotel=scrape_only_hotel, sqlite_name=sqlite_name,
                                               selected_currency=selected_currency, group_adults=group_adults,
                                               num_rooms=num_rooms,
                                               group_children=group_children, check_in='', check_out='',
                                               country=country)

            df = asyncio.run(scraper.scrape_whole_month())

            save_scraped_data(dataframe=df, db=scraper.sqlite_name)

    elif arguments.japan_hotel:
        scraper = JapanScraper(city='', year=2024, month=1, start_day=start_day, nights=nights,
                               scrape_only_hotel=scrape_only_hotel, sqlite_name='',
                               selected_currency=selected_currency, group_adults=group_adults, num_rooms=num_rooms,
                               group_children=group_children, check_in='', check_out='', duckdb_path=duckdb_name,
                               country=country)
        asyncio.run(scraper.scrape_japan_hotels())

    else:
        required_args: list[argparse.Namespace] = [arguments.check_in, arguments.check_out,
                                                   arguments.city, arguments.country]
        if validate_required_args(required_args, ['--check_in', '--check_out', '--city', '--country']):
            check_in: str = arguments.check_in
            check_out: str = arguments.check_out
            city: str = arguments.city

            scraper = BasicGraphQLScraper(city=city, scrape_only_hotel=scrape_only_hotel, sqlite_name=sqlite_name,
                                          selected_currency=selected_currency, group_adults=group_adults,
                                          num_rooms=num_rooms,
                                          group_children=group_children, check_in=check_in, check_out=check_out,
                                          country=country)

            df = asyncio.run(scraper.scrape_graphql())

            save_scraped_data(dataframe=df, db=scraper.sqlite_name)


if __name__ == '__main__':
    main(args)
