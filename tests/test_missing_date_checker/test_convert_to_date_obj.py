import pytest
from datetime import date

from check_missing_dates import convert_to_date_obj


def test_convert_to_date_obj():
    # Test with valid date strings
    input_dates = {'2023-05-15', '2022-12-31', '2024-02-29'}
    expected_output = [date(2023, 5, 15), date(2022, 12, 31), date(2024, 2, 29)]
    actual_output = convert_to_date_obj(input_dates)
    assert sorted(actual_output) == sorted(expected_output)

    # Test with an empty set
    assert convert_to_date_obj(set()) == []

    # Test with invalid date format
    with pytest.raises(ValueError):
        convert_to_date_obj({'2023/05/15'})

    # Test with invalid date
    with pytest.raises(ValueError):
        convert_to_date_obj({'2023-02-30'})