import bs4
import pytest

from japan_avg_hotel_price_finder.scrape import create_df_from_scraped_data


def test_create_df_from_scraped_data():
    check_in = "2024-06-01"
    check_out = "2024-06-05"
    city = "London"
    hotel_data_dict = {
        "Hotel": ["Hotel A", "Hotel B"],
        "Price": [100, 150],
        "Review": [4.5, 4.0]
    }
    df = create_df_from_scraped_data(check_in, check_out, city, hotel_data_dict)
    assert not df.empty

    # Check row
    assert df.shape[0] == 2

    # Check column
    assert df.shape[1] == 7

    check_in = "2024-06-01"
    check_out = "2024-06-05"
    city = "London"
    hotel_data_dict = {}
    df = create_df_from_scraped_data(check_in, check_out, city, hotel_data_dict)
    assert df.empty

    # Check row
    assert df.shape[0] == 0

    # Check column
    assert df.shape[1] == 0


if __name__ == '__main__':
    pytest.main()