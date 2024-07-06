import pandas as pd
import requests
from loguru import logger


def check_info(
        response: requests.Response,
        entered_city: str,
        entered_check_in: str,
        entered_check_out: str,
        entered_selected_currency: str,
        entered_num_adult: int,
        entered_num_children: int,
        entered_num_room: int) -> tuple:
    """
    Get total page number.
    :param response: Requests response.
    :param entered_city: City where the hotels are located.
    :param entered_check_in: Check-in date.
    :param entered_check_out: Check-out date.
    :param entered_selected_currency: Currency of the room price.
    :param entered_num_adult: Number of adults.
    :param entered_num_children: Number of children.
    :param entered_num_room: Number of rooms.
    :return: Total page number and hotel data as a dictionary.
    """
    if response.status_code == 200:
        data = response.json()

        try:
            total_page_num = data['data']['searchQueries']['search']['pagination']['nbResultsTotal']
        except TypeError:
            logger.error("TypeError: Total page number not found.")
            logger.error("Return 0 as total page number")
            total_page_num = 0

        city_data = check_city_data(data)
        selected_currency_data = check_currency_data(data)

        if total_page_num:
            data_mapping = {
                "city": city_data,
                "check_in":
                    data['data']['searchQueries']['search']['flexibleDatesConfig']['dateRangeCalendar']['checkin'][0],
                "check_out":
                    data['data']['searchQueries']['search']['flexibleDatesConfig']['dateRangeCalendar']['checkout'][0],
                "num_adult": data['data']['searchQueries']['search']['searchMeta']['nbAdults'],
                "num_children": data['data']['searchQueries']['search']['searchMeta']['nbChildren'],
                "num_room": data['data']['searchQueries']['search']['searchMeta']['nbRooms'],
                "selected_currency": selected_currency_data
            }

            for key, value in data_mapping.items():
                if locals()[f"entered_{key}"] != value:
                    logger.error(
                        f"Error {key.replace('_', ' ').title()} not match: {locals()[f'entered_{key}']} != {value}")
                    raise SystemExit(
                        f"Error {key.replace('_', ' ').title()} not match: {locals()[f'entered_{key}']} != {value}")
        else:
            data_mapping = {
                "city": 'Not found',
                "check_in": 'Not found',
                "check_out": 'Not found',
                "num_adult": 0,
                "num_children": 0,
                "num_room": 0,
                "selected_currency": 'Not found'
            }
        return total_page_num, data_mapping
    else:
        logger.error(f"Error: {response.status_code}")


def concat_df_list(df_list: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenate a list of Pandas Dataframes.
    :param df_list: A list of Pandas Dataframes.
    :return: Pandas DataFrame.
    """
    logger.info("Concatenate a list of Pandas Dataframes")
    if df_list:
        df_main = pd.concat(df_list)
        return df_main
    else:
        logger.warning("No data was scraped.")
        return pd.DataFrame()


def check_currency_data(data) -> str:
    """
    Check currency data from the GraphQL response.
    :param data: GraphQL response as JSON.
    :return: City name.
    """
    logger.info("Checking currency data from the GraphQL response...")
    selected_currency_data = None
    try:
        for result in data['data']['searchQueries']['search']['results']:
            if 'blocks' in result:
                for block in result['blocks']:
                    if 'finalPrice' in block:
                        selected_currency_data = block['finalPrice']['currency']
                        break
    except KeyError:
        logger.error('KeyError: Currency data not found')
    except IndexError:
        logger.error('IndexError: Currency data not found')
    return selected_currency_data


def check_city_data(data) -> str:
    """
    Check city data from the GraphQL response.
    :param data: GraphQL response as JSON.
    :return: City name.
    """
    logger.info("Checking city data from the GraphQL response...")
    city_data = None
    try:
        for breadcrumb in data['data']['searchQueries']['search']['breadcrumbs']:
            if 'destType' in breadcrumb:
                if breadcrumb['destType'] == 'CITY':
                    city_data = breadcrumb['name']
                    break
    except KeyError:
        logger.error('KeyError: City not found')
    except IndexError:
        logger.error('IndexError: City not found')
    return city_data
