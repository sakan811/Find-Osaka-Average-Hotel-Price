from dataclasses import dataclass


@dataclass
class Details:
    """
    A dataclass designed to encapsulate various parameters required for scraping hotel data.

    Attributes:
        city (str): The city where the hotels are located.
        check_in (str): The check-in date.
                        Only consider this parameter when using Basic GraphQL Scraper.
        check_out (str): The check-out date.
                        Only consider this parameter when using Basic GraphQL Scraper.
        group_adults (str): Number of adults.
        num_rooms (str): Number of rooms.
        group_children (str): Number of children.
        selected_currency (str): Currency of the room price.
        scrape_only_hotel (bool): Whether to scrape only the hotel property data.
        start_day (int): Day to start scraping.
                        Only consider this parameter when using the Whole-Month GraphQL Scraper.
        month (int): Month to start scraping.
                    Only consider this parameter when using Whole-Month GraphQL Scraper.
        year (int): Year to start scraping.
                    Only consider this parameter when using Whole-Month GraphQL Scraper.
        nights (int): Number of nights (Length of stay) which defines the room price.
                    For example, nights = 1 means scraping the hotel with room price for 1 night.
                    Only consider this parameter when using Whole-Month GraphQL Scraper.
        sqlite_name (str): Name of SQLite database to store the scraped data.
    """
    # Set booking details.
    city: str = 'Osaka'
    check_in: str = '2024-11-10'
    check_out: str = '2024-11-11'
    group_adults: int = 1
    num_rooms: int = 1
    group_children: int = 0
    selected_currency: str = 'USD'
    scrape_only_hotel: bool = True

    # Set the start date and number of nights when using Whole-Month GraphQL Scraper
    start_day: int = 1
    month: int = 11
    year: int = 2024
    nights: int = 1

    # Set SQLite database name
    sqlite_name: str = 'avg_japan_hotel_price_test.db'
