import argparse
import asyncio

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.japan_hotel_scraper import JapanScraper
from japan_avg_hotel_price_finder.main_argparse import parse_arguments
from japan_avg_hotel_price_finder.sql.save_to_db import save_scraped_data
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper


def validate_required_args(arguments: argparse.Namespace, required_args: list[str]) -> bool:
    """
    Validate the required arguments.
    :param arguments: Arguments to validate.
    :param required_args: List of required arguments.
    :return: Boolean.
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
        scrape_only_hotel=arguments.scrape_only_hotel, sqlite_name=arguments.sqlite_name,
        selected_currency=arguments.selected_currency, group_adults=arguments.group_adults,
        num_rooms=arguments.num_rooms, group_children=arguments.group_children, check_in='', check_out='',
        country=arguments.country
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
