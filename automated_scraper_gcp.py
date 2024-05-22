from datetime import datetime

import functions_framework

from automated_scraper import automated_scraper_main
from set_details import Details


@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    # Define booking parameters for the hotel search.
    city = 'Osaka'
    group_adults = 1
    num_rooms = 1
    group_children = 0
    selected_currency = 'USD'

    today = datetime.today()
    start_day: int = 1
    year: int = today.year

    details = Details(
        city=city, group_adults=group_adults, num_rooms=num_rooms, group_children=group_children,
        selected_currency=selected_currency, start_day=start_day, year=year
    )
    for month in (1, 13):
        automated_scraper_main(month, details)
