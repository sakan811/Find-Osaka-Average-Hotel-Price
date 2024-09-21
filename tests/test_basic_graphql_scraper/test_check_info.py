import pydantic
import pytest

from japan_avg_hotel_price_finder.graphql_scraper import BasicGraphQLScraper


@pytest.mark.asyncio
async def test_returns_correct_total_page_number_and_data_mapping():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-01-01'],
                            'checkout': ['2023-01-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 1,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = "Test Country"
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = False

    # When
    scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                  selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                  group_children=entered_num_children, num_rooms=entered_num_room,
                                  scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
    scraper.data = data

    result = await scraper.check_info()

    # Then
    assert result == 1


@pytest.mark.asyncio
async def test_handles_response_with_missing_or_null_fields_gracefully():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': None, 'destType': 'CITY'}],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': [None],
                            'checkout': [None]
                        }
                    },
                    'searchMeta': {
                        'nbAdults': None,
                        'nbChildren': None,
                        'nbRooms': None
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': None}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = "Test Country"
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    with pytest.raises(pydantic.ValidationError):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()


@pytest.mark.asyncio
async def test_handles_response_with_currency_is_none():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ["2023-01-01"],
                            'checkout': ["2023-01-02"]
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 1,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': None}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    with pytest.raises(pydantic.ValidationError):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()


@pytest.mark.asyncio
async def test_data_mapping_check_in_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-02-01'],
                            'checkout': ['2023-01-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 1,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()


@pytest.mark.asyncio
async def test_data_mapping_check_out_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-01-01'],
                            'checkout': ['2023-02-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 1,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()


@pytest.mark.asyncio
async def test_data_mapping_adult_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-01-01'],
                            'checkout': ['2023-02-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 10,
                        'nbChildren': 1,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()


@pytest.mark.asyncio
async def test_data_mapping_room_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-01-01'],
                            'checkout': ['2023-02-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 1,
                        'nbRooms': 10
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()


@pytest.mark.asyncio
async def test_data_mapping_children_not_match():
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-01-01'],
                            'checkout': ['2023-02-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 10,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()


@pytest.mark.asyncio
async def test_data_mapping_currency_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-01-01'],
                            'checkout': ['2023-02-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 1,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'GBP'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()


@pytest.mark.asyncio
async def test_data_mapping_city_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Tokyo', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-01-01'],
                            'checkout': ['2023-02-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 1,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()


@pytest.mark.asyncio
async def test_total_page_num_is_zero():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 0},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-01-01'],
                            'checkout': ['2023-01-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 1,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = True

    # When
    scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                  selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                  group_children=entered_num_children, num_rooms=entered_num_room,
                                  scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
    scraper.data = data
    result = await scraper.check_info()

    # Then
    assert result == 0


@pytest.mark.asyncio
async def test_data_mapping_hotel_filter_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [
                        {'name': 'Test Country', 'destType': 'COUNTRY'},
                        {'name': 'Test City', 'destType': 'CITY'}
                    ],
                    'flexibleDatesConfig': {
                        'dateRangeCalendar': {
                            'checkin': ['2023-01-01'],
                            'checkout': ['2023-01-02']
                        }
                    },
                    'searchMeta': {
                        'nbAdults': 2,
                        'nbChildren': 1,
                        'nbRooms': 1
                    },
                    'results': [{
                        'blocks': [{
                            'finalPrice': {'currency': 'USD'}
                        }]
                    }]
                }
            }
        }
    }
    entered_city = "Test City"
    entered_country = 'Test Country'
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1
    entered_hotel_filter = False

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room,
                                      scrape_only_hotel=entered_hotel_filter, country=entered_country, sqlite_name='')
        scraper.data = data
        await scraper.check_info()

if __name__ == '__main__':
    pytest.main()
