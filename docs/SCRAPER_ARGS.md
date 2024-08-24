## Scraper's Arguments
### `--scraper`
- **Type**: `bool`
- **Default**: `True`
- **Description**: Determines whether to use the basic GraphQL scraper. By default, this is set to `True`.

### `--whole_mth`
- **Type**: `bool`
- **Default**: `False`
- **Description**: If set to `True`, the Whole-Month GraphQL scraper is used. The default value is `False`.

### `--city`
- **Type**: `str`
- **Description**: Specifies the city where the hotels are located.

### `--country`
- **Type**: `str`
- **Description**: Specifies the country where the hotels are located. Default is Japan.

### `--check_in`
- **Type**: `str`
- **Description**: The check-in date for the hotel stay. The date should be in `YYYY-MM-DD` format.

### `--check_out`
- **Type**: `str`
- **Description**: The check-out date for the hotel stay. The date should be in `YYYY-MM-DD` format.

### `--group_adults`
- **Type**: `int`
- **Default**: `1`
- **Description**: Specifies the number of adults in the group. The default value is `1`.

### `--num_rooms`
- **Type**: `int`
- **Default**: `1`
- **Description**: Specifies the number of rooms required for the group. The default value is `1`.

### `--group_children`
- **Type**: `int`
- **Default**: `0`
- **Description**: Specifies the number of children in the group. The default value is `0`.

### `--selected_currency`
- **Type**: `str`
- **Default**: `'USD'`
- **Description**: The currency for the room prices. By default, this is set to `'USD'`.

### `--scrape_only_hotel`
- **Type**: `bool`
- **Default**: `True`
- **Description**: If set to `True`, the scraper will only target hotel properties. The default value is `True`.

### `--sqlite_name`
- **Type**: `str`
- **Default**: `'avg_japan_hotel_price_test.db'`
- **Description**: The name of the SQLite database file to use. The default value is `'avg_japan_hotel_price_test.db'`.

### `--year`
- **Type**: `int`
- **Description**: Specifies the year to scrape. This argument is required for Whole-Month Scraper.

### `--month`
- **Type**: `int`
- **Description**: Specifies the month to scrape. This argument is required for Whole-Month Scraper.

### `--start_day`
- **Type**: `int`
- **Default**: `1`
- **Description**: Specifies the day of the month to start scraping from. The default value is `1`.

### `--nights`
- **Type**: `int`
- **Default**: `1`
- **Description**: Specifies the length of stay in nights. The default value is `1`.