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
        "--sqlite_name", "test.db"
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
    assert args.sqlite_name == "test.db"
    assert args.duckdb_name is None


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
        "--sqlite_name", "test.db"
    ]

    monkeypatch.setattr(sys, 'argv', test_args)
    with pytest.raises(SystemExit):
        parse_arguments()


def test_conflicting_arguments(monkeypatch):
    # Conflicting database arguments
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
        "--sqlite_name", "test.db",
        "--duckdb_name", "test.duckdb"
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
        "--sqlite_name", "test.db"
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
        "--sqlite_name", "test.db"
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
        "--duckdb_name", "test.duckdb"
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
    assert args.sqlite_name is None
    assert args.duckdb_name == "test.duckdb"


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
        "--sqlite_name", "test.db",
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
    assert args.sqlite_name == "test.db"
    assert args.duckdb_name is None
    assert args.year == 2024
    assert args.month == 1
