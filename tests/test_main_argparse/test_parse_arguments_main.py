import sys
import pytest
from japan_avg_hotel_price_finder.main_argparse import parse_arguments


def test_parse_arguments(monkeypatch):
    # Valid arguments for basic scraper
    test_args = [
        "main.py",
        "--scraper",
        "--city", "Tokyo",
        "--country", "Japan",
        "--check_in", "2024-01-01",
        "--check_out", "2024-01-02",
        "--group_adults", "2",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel",
    ]

    monkeypatch.setattr(sys, 'argv', test_args)
    args = parse_arguments()

    assert args.scraper is True
    assert args.city == "Tokyo"
    assert args.country == "Japan"
    assert args.check_in == "2024-01-01"
    assert args.check_out == "2024-01-02"
    assert args.group_adults == 2
    assert args.num_rooms == 1
    assert args.group_children == 0
    assert args.selected_currency == "USD"
    assert args.scrape_only_hotel is True


def test_missing_required_arguments(monkeypatch):
    # Missing required scraper argument
    test_args = [
        "main.py",
        "--city", "Tokyo",
        "--country", "Japan",
        "--check_in", "2024-01-01",
        "--check_out", "2024-01-02",
        "--group_adults", "2",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel",
    ]

    monkeypatch.setattr(sys, 'argv', test_args)
    with pytest.raises(SystemExit):
        parse_arguments()


def test_invalid_argument_types(monkeypatch):
    # Invalid type for group_adults
    test_args = [
        "main.py",
        "--scraper",
        "--city", "Tokyo",
        "--country", "Japan",
        "--check_in", "2024-01-01",
        "--check_out", "2024-01-02",
        "--group_adults", "two",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel",
    ]

    monkeypatch.setattr(sys, 'argv', test_args)
    with pytest.raises(SystemExit):
        parse_arguments()


def test_boundary_values(monkeypatch):
    # Boundary value for group_adults
    test_args = [
        "main.py",
        "--scraper",
        "--city", "Tokyo",
        "--country", "Japan",
        "--check_in", "2024-01-01",
        "--check_out", "2024-01-02",
        "--group_adults", "0",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel",
    ]

    monkeypatch.setattr(sys, 'argv', test_args)
    with pytest.raises(SystemExit):
        parse_arguments()


def test_valid_japan_scraper_arguments(monkeypatch):
    # Valid arguments for Japan scraper
    test_args = [
        "main.py",
        "--japan_hotel",
        "--city", "Tokyo",
        "--country", "Japan",
        "--check_in", "2024-01-01",
        "--check_out", "2024-01-02",
        "--group_adults", "2",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel",
    ]

    monkeypatch.setattr(sys, 'argv', test_args)
    args = parse_arguments()

    assert args.japan_hotel is True
    assert args.city == "Tokyo"
    assert args.country == "Japan"
    assert args.check_in == "2024-01-01"
    assert args.check_out == "2024-01-02"
    assert args.group_adults == 2
    assert args.num_rooms == 1
    assert args.group_children == 0
    assert args.selected_currency == "USD"
    assert args.scrape_only_hotel is True


def test_valid_whole_month_scraper_arguments(monkeypatch):
    # Valid arguments for Whole-Month scraper
    test_args = [
        "main.py",
        "--whole_mth",
        "--city", "Tokyo",
        "--country", "Japan",
        "--check_in", "2024-01-01",
        "--check_out", "2024-01-02",
        "--group_adults", "2",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel",
        "--year", "2024",
        "--month", "1"
    ]

    monkeypatch.setattr(sys, 'argv', test_args)
    args = parse_arguments()

    assert args.whole_mth is True
    assert args.city == "Tokyo"
    assert args.country == "Japan"
    assert args.check_in == "2024-01-01"
    assert args.check_out == "2024-01-02"
    assert args.group_adults == 2
    assert args.num_rooms == 1
    assert args.group_children == 0
    assert args.selected_currency == "USD"
    assert args.scrape_only_hotel is True
    assert args.year == 2024
    assert args.month == 1


def test_japan_arguments(monkeypatch):
    # Test case for add_japan_arguments and validate_japan_arguments
    test_args = [
        "main.py",
        "--japan_hotel",
        "--prefecture", "Tokyo", "Osaka",
        "--city", "Tokyo",
        "--country", "Japan",
        "--check_in", "2024-01-01",
        "--check_out", "2024-01-02",
        "--group_adults", "2",
        "--num_rooms", "1",
        "--group_children", "0",
        "--selected_currency", "USD",
        "--scrape_only_hotel",
    ]

    monkeypatch.setattr(sys, 'argv', test_args)
    args = parse_arguments()

    # Test that add_japan_arguments worked correctly
    assert args.prefecture == ["Tokyo", "Osaka"]

    # Test that validate_japan_arguments doesn't raise an error
    # (If it did, parse_arguments would have raised a SystemExit)
    assert args.japan_hotel is True

    # Test other arguments to ensure everything else is still correct
    assert args.city == "Tokyo"
    assert args.country == "Japan"
    assert args.check_in == "2024-01-01"
    assert args.check_out == "2024-01-02"
    assert args.group_adults == 2
    assert args.num_rooms == 1
    assert args.group_children == 0
    assert args.selected_currency == "USD"
    assert args.scrape_only_hotel is True