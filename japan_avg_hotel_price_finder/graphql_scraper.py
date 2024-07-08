import asyncio

import aiohttp
import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from japan_avg_hotel_price_finder.graphql_scraper_func.graphql_data_extractor import extract_hotel_data
from japan_avg_hotel_price_finder.graphql_scraper_func.graphql_data_transformer import transform_data_in_df
from japan_avg_hotel_price_finder.graphql_scraper_func.graphql_request_func import get_header, get_graphql_query, \
    fetch_hotel_data
from japan_avg_hotel_price_finder.graphql_scraper_func.graphql_utils_func import check_info, concat_df_list

logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')


async def scrape_graphql(
        city: str = None,
        check_in: str = None,
        check_out: str = None,
        selected_currency: str = None,
        group_adults: int = 1,
        num_rooms: int = 1,
        group_children: int = 0,
        hotel_filter: bool = False) -> pd.DataFrame:
    """
    Scrape hotel data from GraphQL endpoint using async.
    """
    logger.info("Start scraping data from GraphQL endpoint")
    logger.info(f"City: {city} | Check-in: {check_in} | Check-out: {check_out} | Currency: {selected_currency}")
    logger.info(f"Adults: {group_adults} | Children: {group_children} | Rooms: {num_rooms}")
    logger.info(f"Only hotel properties: {hotel_filter}")

    if city and check_in and check_out and selected_currency:
        url = f'https://www.booking.com/dml/graphql?selected_currency={selected_currency}'
        headers = get_header()
        graphql_query = get_graphql_query(city=city, check_in=check_in, check_out=check_out, group_adults=group_adults,
                                          group_children=group_children, num_rooms=num_rooms, hotel_filter=hotel_filter)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=graphql_query) as response:
                if response.status == 200:
                    data = await response.json()
                    total_page_num, hotel_data_dict = await check_info(
                        data, city, check_in, check_out, selected_currency, group_adults, group_children, num_rooms
                    )
                else:
                    logger.error(f"Error: {response.status}")
                    return pd.DataFrame()

        logger.debug(f"Total page number: {total_page_num}")
        logger.debug(f"City: {hotel_data_dict['city']}")
        logger.debug(f"Check-in date: {hotel_data_dict['check_in']}")
        logger.debug(f"Check-out date: {hotel_data_dict['check_out']}")
        logger.debug(f"Number of adults: {hotel_data_dict['num_adult']}")
        logger.debug(f"Number of children: {hotel_data_dict['num_children']}")
        logger.debug(f"Number of rooms: {hotel_data_dict['num_room']}")
        logger.debug(f"Currency: {hotel_data_dict['selected_currency']}")

        if total_page_num:
            df_list = []
            logger.info("Scraping data from GraphQL endpoint...")

            async with aiohttp.ClientSession() as session:
                tasks = []
                for offset in range(0, total_page_num, 100):
                    graphql_query = get_graphql_query(city=city, check_in=check_in, check_out=check_out,
                                                      group_adults=group_adults,
                                                      group_children=group_children, num_rooms=num_rooms,
                                                      hotel_filter=hotel_filter,
                                                      page_offset=offset)
                    tasks.append(fetch_hotel_data(session, url, headers, graphql_query))

                results = await asyncio.gather(*tasks)

            for hotel_data_list in results:
                if hotel_data_list:
                    extract_hotel_data(df_list, hotel_data_list)

            if df_list:
                df = concat_df_list(df_list)
                return transform_data_in_df(check_in, city, df)
            else:
                logger.warning("No hotel data was found. Return an empty DataFrame.")
                return pd.DataFrame()
        else:
            logger.warning("Total page number not found. Return an empty DataFrame.")
            return pd.DataFrame()
    else:
        logger.warning("Error: city, check_in, check_out and selected_currency are required")
        return pd.DataFrame()


if __name__ == '__main__':
    pass
