import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file

logger = configure_logging_with_file(log_dir='logs', log_file='graphql_utils_func.log',
                                     logger_name='graphql_utils_func')


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


def check_hotel_filter_data(data) -> bool:
    """
    Check hotel filter data from the GraphQL response.
    :param data: GraphQL response as JSON.
    :return: Hotel filter indicator.
    """
    logger.info("Checking hotel filter data from the GraphQL response...")

    try:
        for option in data['data']['searchQueries']['search']['appliedFilterOptions']:
            logger.debug(f'Filter options: {option}')
            if 'urlId' in option:
                if option['urlId'] == "ht_id=204":
                    return True
    except KeyError:
        logger.error('KeyError: hotel_filter not found')
        return False
    except IndexError:
        logger.error('IndexError: hotel_filter not found')
        return False

    return False
