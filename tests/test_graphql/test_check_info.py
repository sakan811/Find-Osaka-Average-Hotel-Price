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
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
                                  scrape_only_hotel=entered_hotel_filter)
    result = await scraper.check_info(data)

    # Then
    assert result == (1, {
        "city": "Test City",
        "check_in": "2023-01-01",
        "check_out": "2023-01-02",
        "group_adults": 2,
        "group_children": 1,
        "num_rooms": 1,
        'scrape_only_hotel': False,
        "selected_currency": "USD"
    })


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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    # When
    error_message = ''
    try:
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room)
        result = await scraper.check_info(data)
    except SystemExit as e:
        error_message = str(e)

    # Then
    assert error_message == "Error City not match: Test City != None"


@pytest.mark.asyncio
async def test_handles_response_with_currency_is_none():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    # When
    error_message = ''
    try:
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room)
        result = await scraper.check_info(data)
    except SystemExit as e:
        error_message = str(e)

    # Then
    assert error_message == "Error Selected Currency not match: USD != None"


@pytest.mark.asyncio
async def test_data_mapping_check_in_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room)
        result = await scraper.check_info(data)


@pytest.mark.asyncio
async def test_data_mapping_check_out_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room)
        result = await scraper.check_info(data)


@pytest.mark.asyncio
async def test_data_mapping_adult_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room)
        result = await scraper.check_info(data)


@pytest.mark.asyncio
async def test_data_mapping_room_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room)
        result = await scraper.check_info(data)


@pytest.mark.asyncio
async def test_data_mapping_children_not_match():
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room)
        result = await scraper.check_info(data)


@pytest.mark.asyncio
async def test_data_mapping_currency_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room)
        result = await scraper.check_info(data)


@pytest.mark.asyncio
async def test_data_mapping_city_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': 'Tokyo', 'destType': 'CITY'}],
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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    with pytest.raises(SystemExit):
        scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                      selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                      group_children=entered_num_children, num_rooms=entered_num_room)
        result = await scraper.check_info(data)


@pytest.mark.asyncio
async def test_total_page_num_is_zero():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'pagination': {'nbResultsTotal': 0},
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
    entered_check_in = "2023-01-01"
    entered_check_out = "2023-01-02"
    entered_selected_currency = "USD"
    entered_num_adult = 2
    entered_num_children = 1
    entered_num_room = 1

    # When
    scraper = BasicGraphQLScraper(city=entered_city, check_in=entered_check_in, check_out=entered_check_out,
                                  selected_currency=entered_selected_currency, group_adults=entered_num_adult,
                                  group_children=entered_num_children, num_rooms=entered_num_room)
    result = await scraper.check_info(data)

    # Then
    assert result == (0, {
        "city": 'Not found',
        "check_in": 'Not found',
        "check_out": 'Not found',
        "num_adult": 0,
        "num_children": 0,
        "num_room": 0,
        "selected_currency": 'Not found'
    })


@pytest.mark.asyncio
async def test_data_mapping_hotel_filter_not_match():
    # Given
    data = {
        'data': {
            'searchQueries': {
                'search': {
                    'appliedFilterOptions': [{'urlId': "ht_id=204"}],
                    'pagination': {'nbResultsTotal': 1},
                    'breadcrumbs': [{}, {}, {'name': 'Test City', 'destType': 'CITY'}],
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
                                      scrape_only_hotel=entered_hotel_filter)
        result = await scraper.check_info(data)

if __name__ == '__main__':
    pytest.main()
