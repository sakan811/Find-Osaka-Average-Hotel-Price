import argparse
import asyncio

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from japan_avg_hotel_price_finder.utils import check_in_db_if_all_date_was_scraped, \
    check_in_csv_dir_if_all_date_was_scraped

logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')


async def check_missing_dates_main():
    parser = argparse.ArgumentParser(description='Parser that control which kind of missing dates checkers to use.')
    parser.add_argument('--check_db', type=str, default=False, help='Check missing dates in database')
    parser.add_argument('--check_csv', type=str, default=False, help='Check missing dates in CSV file directory')

    args = parser.parse_args()

    if args.check_db:
        db = args.check_db
        await check_in_db_if_all_date_was_scraped(db=db, to_sqlite=True)
    elif args.check_csv:
        directory = args.check_csv
        directory = str(directory)
        await check_in_csv_dir_if_all_date_was_scraped(directory)
    else:
        logger.warning('Please use --check_db or --check_csv')


if __name__ == '__main__':
    asyncio.run(check_missing_dates_main())
