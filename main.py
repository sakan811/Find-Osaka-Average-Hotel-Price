import argparse
import asyncio
from datetime import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

from japan_avg_hotel_price_finder.configure_logging import main_logger
from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper
from japan_avg_hotel_price_finder.japan_hotel_scraper import JapanScraper
from japan_avg_hotel_price_finder.main_argparse import parse_arguments
from japan_avg_hotel_price_finder.sql.save_to_db import save_scraped_data
from japan_avg_hotel_price_finder.whole_mth_graphql_scraper import WholeMonthGraphQLScraper

load_dotenv(dotenv_path='.env', override=True)


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


def run_whole_month_scraper(arguments: argparse.Namespace, engine: Engine) -> None:
    """
    Run the Whole-Month GraphQL scraper
    :param arguments: Arguments to pass to the scraper
    :param engine: SQLAlchemy engine
    :return: None
    """
    required_args = ['year', 'month', 'city', 'country']
    if validate_required_args(arguments, required_args):
        scraper = WholeMonthGraphQLScraper(
            city=arguments.city, year=arguments.year, month=arguments.month, start_day=arguments.start_day,
            nights=arguments.nights, scrape_only_hotel=arguments.scrape_only_hotel,
            selected_currency=arguments.selected_currency, group_adults=arguments.group_adults,
            num_rooms=arguments.num_rooms, group_children=arguments.group_children, check_in='', check_out='',
            country=arguments.country
        )
        df = asyncio.run(scraper.scrape_whole_month())
        save_scraped_data(dataframe=df, engine=engine)


def run_japan_hotel_scraper(arguments: argparse.Namespace, engine: Engine) -> None:
    """
    Run the Japan hotel scraper
    :param arguments: Arguments to pass to the scraper
    :param engine: SQLAlchemy engine
    :return: None
    """
    if arguments.prefecture:
        city = ','.join(arguments.prefecture)
    else:
        city = ''

    year: int = datetime.now().year
    
    # Get start and end months from arguments
    start_month = arguments.start_month
    end_month = arguments.end_month
    
    # Set default currency to USD if not provided
    selected_currency = arguments.selected_currency if arguments.selected_currency else 'USD'
    
    scraper = JapanScraper(
        city=city, year=year, month=start_month, start_day=arguments.start_day, nights=arguments.nights,
        scrape_only_hotel=arguments.scrape_only_hotel, selected_currency=selected_currency,
        group_adults=arguments.group_adults, num_rooms=arguments.num_rooms, group_children=arguments.group_children,
        check_in='', check_out='', country=arguments.country, engine=engine,
        start_month=start_month, end_month=end_month
    )
    asyncio.run(scraper.scrape_japan_hotels())


def run_basic_scraper(arguments: argparse.Namespace, engine: Engine) -> None:
    """
    Run the Basic GraphQL scraper
    :param arguments: Arguments to pass to the scraper
    :param engine: SQLAlchemy engine
    :return: None
    """
    required_args = ['check_in', 'check_out', 'city', 'country']
    if validate_required_args(arguments, required_args):
        scraper = BasicGraphQLScraper(
            city=arguments.city, scrape_only_hotel=arguments.scrape_only_hotel,
            selected_currency=arguments.selected_currency, group_adults=arguments.group_adults,
            num_rooms=arguments.num_rooms, group_children=arguments.group_children, check_in=arguments.check_in,
            check_out=arguments.check_out, country=arguments.country
        )
        df = asyncio.run(scraper.scrape_graphql())
        save_scraped_data(dataframe=df, engine=engine)


def main() -> None:
    """
    Main function to run the scraper
    :return: None
    """
    arguments = parse_arguments()
    postgres_url = (f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
                    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")
    engine = create_engine(postgres_url)

    if arguments.whole_mth:
        run_whole_month_scraper(arguments, engine)
    elif arguments.japan_hotel:
        run_japan_hotel_scraper(arguments, engine)
    else:
        run_basic_scraper(arguments, engine)


if __name__ == '__main__':
    main()
