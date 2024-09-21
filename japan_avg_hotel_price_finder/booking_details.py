from pydantic import BaseModel, Field


class BookingDetails(BaseModel):
    """
    Data class to store booking details.

    Attributes:
    - city (str): City where the hotels are located.
    - country (str): Country where the city is located.
    - check_in (str): Check-in date.
    - check_out (str): Check-out date.
    - group_adults (int): Number of adults.
    - num_rooms (int): Number of rooms.
    - group_children (int): Number of children.
    - selected_currency (str): Room price currency.
    - scrape_only_hotel (bool): Whether to scrape only hotel.
    - sqlite_name (str): Path to SQLite database.
    """
    city: str = ''
    country: str = ''
    check_in: str = ''
    check_out: str = ''
    group_adults: int = Field(1, gt=0)
    num_rooms: int = Field(1, gt=0)
    group_children: int = Field(0, ge=0)
    selected_currency: str = ''
    scrape_only_hotel: bool = True
    sqlite_name: str = ''