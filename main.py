from loguru import logger

from japan_avg_hotel_price_finder.scrape_each_date import ScrapeEachDate

logger.add('japan_avg_hotel_price_month.log',
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {name} | {module} | {function} | {line} | {message}",
           mode='w')

city = 'Osaka'
group_adults = '1'
num_rooms = '1'
group_children = '0'
selected_currency = 'USD'

scrape_each_date = ScrapeEachDate(city, group_adults, num_rooms, group_children, selected_currency)
scrape_each_date.scrape_until_month_end(1, 6, 2024, 1)
