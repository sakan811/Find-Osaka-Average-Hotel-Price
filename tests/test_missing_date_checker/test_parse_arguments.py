import sys
import pytest
from check_missing_dates import parse_arguments


def test_valid_arguments(monkeypatch):
    test_args = [
        "check_missing_dates.py",
        "--city", "Tokyo",
        "--group_adults", "2",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel", "True",
        "--sqlite_name", "test.db",
        "--year", "2024"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)
    args = parse_arguments()

    assert args.city == "Tokyo"
    assert args.group_adults == 2
    assert args.num_rooms == 1
    assert args.group_children == 0
    assert args.selected_currency == "USD"
    assert args.scrape_only_hotel is True
    assert args.sqlite_name == "test.db"
    assert args.year == 2024


def test_missing_required_arguments(monkeypatch):
    test_args = [
        "check_missing_dates.py",
        "--group_adults", "2",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel", "True",
        "--sqlite_name", "test.db",
        "--year", "2024"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)
    with pytest.raises(SystemExit):
        parse_arguments()


def test_invalid_argument_types(monkeypatch):
    test_args = [
        "check_missing_dates.py",
        "--city", "Tokyo",
        "--group_adults", "two",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel", "True",
        "--sqlite_name", "test.db",
        "--year", "2024"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)
    with pytest.raises(SystemExit):
        parse_arguments()


def test_boundary_values(monkeypatch):
    test_args = [
        "check_missing_dates.py",
        "--city", "Tokyo",
        "--group_adults", "0",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel", "True",
        "--sqlite_name", "test.db",
        "--year", "2024"
    ]
    monkeypatch.setattr(sys, 'argv', test_args)
    args = parse_arguments()

    assert args.group_adults == 0
