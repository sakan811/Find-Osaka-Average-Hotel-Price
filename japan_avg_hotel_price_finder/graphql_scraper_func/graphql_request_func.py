import os

from aiohttp import ClientSession
from dotenv import load_dotenv

from japan_avg_hotel_price_finder.configure_logging import main_logger

# Load environment variables from .env file
load_dotenv()


def get_header() -> dict:
    """
    Return header.
    :return: Header as a dictionary.
    """
    main_logger.info("Getting header...")
    return {
        "User-Agent": os.getenv("USER_AGENT"),
    }


async def fetch_hotel_data(session: ClientSession, url: str, headers: dict, graphql_query: dict) -> list:
    """
    Fetch hotel data from GraphQL response.
    :param session: client session.
    :param url: Url to fetch data from.
    :param headers: Request headers.
    :param graphql_query: GraphQL query.
    :return: List of hotel data.
    """
    async with session.post(url, headers=headers, json=graphql_query) as response:
        if response.status == 200:
            data = await response.json()
            try:
                return data['data']['searchQueries']['search']['results']
            except (ValueError, KeyError) as e:
                main_logger.error(f"Error extracting hotel data: {e}")
                return []
            except Exception as e:
                main_logger.error(f"Unexpected error: {e}")
                return []
        else:
            main_logger.error(f"Error: {response.status}")
            return []
