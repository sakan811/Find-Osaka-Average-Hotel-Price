from datetime import date, datetime

from check_missing_dates import filter_past_date


def test_filter_past_date():
    # Setup
    today = datetime(2023, 5, 15)

    # Test with mix of past, present, and future dates
    input_dates = [
        date(2023, 5, 14),  # past
        date(2023, 5, 15),  # present
        date(2023, 5, 16),  # future
        date(2022, 12, 31),  # past
        date(2024, 1, 1),  # future
    ]
    expected_output = [
        date(2023, 5, 15),
        date(2023, 5, 16),
        date(2024, 1, 1),
    ]
    assert filter_past_date(input_dates, today) == expected_output

    # Test with all past dates
    all_past = [date(2023, 5, 14), date(2023, 5, 13), date(2023, 5, 12)]
    assert filter_past_date(all_past, today) == []

    # Test with all future dates
    all_future = [date(2023, 5, 16), date(2023, 5, 17), date(2023, 5, 18)]
    assert filter_past_date(all_future, today) == all_future

    # Test with empty list
    assert filter_past_date([], today) == []

    # Test with only today's date
    assert filter_past_date([today.date()], today) == [today.date()]