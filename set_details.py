from dataclasses import dataclass

@dataclass
class Details:
    """
    A class to hold the details of the hotel and date to scrape.

    Attributes:
        city (str): The city where the hotels are located.
        group_adults (str): Number of adults.
        num_rooms (str): Number of rooms.
        group_children (str): Number of children.
        selected_currency (str): Currency of the room price.
        start_day (int): Day to start scraping.
        month (int): Month to start scraping.
        year (int): Year to start scraping.
        nights (int): Number of nights (Length of stay) which defines the room price.
                    For example, nights = 1 means scraping the hotel with room price for 1 night.
    """
    # Define booking parameters for the hotel search.
    city: str = 'Osaka'
    group_adults: str = '1'
    num_rooms: str = '1'
    group_children: str = '0'
    selected_currency: str = 'USD'

    # Specify the start date and duration of stay for data scraping
    start_day: int = 1
    month: int = 12
    year: int = 2024
    nights: int = 1
