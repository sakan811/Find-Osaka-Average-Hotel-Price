#    Copyright 2024 Sakan Nirattisaykul
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import datetime
import re
import time

import bs4
import pandas as pd
from loguru import logger
from pandas import DataFrame
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from japan_avg_hotel_price_finder.migrate_to_sqlite import migrate_data_to_sqlite
from set_details import Details


class BasicScraper:
    def __init__(self, details: Details):
        """
        Initialize the Scraper class with the following parameter:
        :param  details: Details dataclass object
        """
        self.details = details

    @staticmethod
    def _click_pop_up_ad(wait: WebDriverWait, driver: WebDriver) -> None:
        """
        Click pop-up ad.
        :param driver: Selenium WebDriver.
        :param wait: Selenium WebDriverWait object.
        :return: None
        """
        logger.info("Clicking pop-up ad...")

        ads_css_selector = ('#b2searchresultsPage > div.b9720ed41e.cdf0a9297c > div > div > div > div.dd5dccd82f > '
                            'div.ffd93a9ecb.dc19f70f85.eb67815534 > div > button')
        try:
            time.sleep(2)
            ads = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ads_css_selector)))
            ads.click()
        except NoSuchElementException as e:
            logger.error(e)
            logger.error(f'{ads_css_selector} not found')
        except TimeoutException as e:
            logger.error(e)
            logger.error(f'{ads_css_selector} timed out')
            driver.refresh()
            logger.info('Refreshed page')
        except Exception as e:
            logger.error(e)
            logger.error(f'{ads_css_selector} failed due to {e}')
        else:
            logger.info('Clicked the pop-up ads successfully')

    @staticmethod
    def _click_load_more_result_button(driver: WebDriver) -> None:
        """
        Click 'load more result' button to load more hotels.
        :param driver: Selenium WebDriver.
        :return: None
        """
        logger.info("Clicking 'load more result' button...")

        load_more_result_css_selector = ('#bodyconstraint-inner > div:nth-child(8) > div > div.af5895d4b2 > '
                                         'div.df7e6ba27d > div.bcbf33c5c3 > div.dcf496a7b9.bb2746aad9 > '
                                         'div.d4924c9e74 > div.c82435a4b8.f581fde0b8 > button')

        try:
            load_more_button = driver.find_element(By.CSS_SELECTOR, load_more_result_css_selector)
            load_more_button.click()
        except NoSuchElementException as e:
            logger.error(e)
            logger.error(f'{load_more_result_css_selector} not found. Keep scrolling.')
        except StaleElementReferenceException as e:
            logger.error(e)
            logger.error(f'{load_more_result_css_selector} is no longer valid '
                         f'because it has been modified or removed from the DOM.')
        except Exception as e:
            logger.error(e)
            logger.error(f'{load_more_result_css_selector} failed due to {e}')
        else:
            logger.info(f'{load_more_result_css_selector} clicked successfully')

    def _scroll_down_until_page_bottom(self, driver: WebDriver) -> None:
        """
        Scroll down and click 'Load more result' button if present.

        Scroll down until reach the bottom of the page.
        :param driver: Selenium WebDriver.
        :return: None
        """
        logger.info("Scrolling down until the bottom of the page...")
        logger.info("Click 'Load more result' button if present.")
        while True:
            # Get current height
            current_height = driver.execute_script("return window.scrollY")
            logger.debug(f'{current_height = }')

            # Scroll down to the bottom
            driver.execute_script("window.scrollBy(0, 2000);")

            # Wait for some time to load more content (adjust as needed)
            time.sleep(1)

            # Get current height
            new_height = driver.execute_script("return window.scrollY")
            logger.debug(f'{new_height = }')

            # If the new height is the same as the last height, then the bottom is reached
            if current_height == new_height:
                logger.info("Reached the bottom of the page.")
                break

            time.sleep(2)

            self._click_load_more_result_button(driver)

    @staticmethod
    def _scrape_data_from_box_class(
            soup: bs4.BeautifulSoup,
            box_class: str,
            hotel_class: str,
            price_class: str,
            review_class: str,
            data: pd.DataFrame) -> None:
        """
        Scrape data from box class.
        :param soup: bs4.BeautifulSoup object.
        :param box_class: Class name of the box that contains the hotel data.
        :param hotel_class: Class name of the hotel name data.
        :param price_class: Class name of the price data.
        :param review_class: Class name of the review score data.
        :param data: Pandas dataframe.
        :return: None
        """
        logger.info("Scraping data from box class...")

        # Find the box elements
        box_elements = soup.select(f'.{box_class}')

        for box_element in box_elements:
            # Find the elements within the box element
            hotel_element = box_element.select(f'.{hotel_class}')
            price_element = box_element.select(f'.{price_class}')
            review_element = box_element.select(f'.{review_class}')

            # Check if all elements are presented before extracting data
            if hotel_element and price_element and review_element:
                hotel_name = hotel_element[0].text
                price = re.sub(r'[^0-9]', '', price_element[0].text)
                review_score = review_element[0].text.split()[1]

                data['Hotel'].append(hotel_name)
                data['Price'].append(price)
                data['Review'].append(review_score)

                logger.info(f'All elements are presented.')
                logger.debug(f'Hotel: {hotel_element}')
                logger.debug(f'Price: {price_element}')
                logger.debug(f'Review Score: {review_element}')
            else:
                logger.warning(f'Not all elements are presented.')
                logger.debug(f'Hotel: {hotel_element}')
                logger.debug(f'Price: {price_element}')
                logger.debug(f'Review Score: {review_element}')

    def _scrape(self, url: str, data) -> None:
        """
        Scrape hotel data from the website.
        :param url: Website URL.
        :param data: Empty Dictionary.
        :return: None
        """
        # Configure Chrome options to block image loading and disable automation features
        options = webdriver.ChromeOptions()

        chrome_prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", chrome_prefs)

        # Disable blink features related to automation control
        options.add_argument('--disable-blink-features=AutomationControlled')

        # Initialize the Chrome driver with the configured options
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        wait = WebDriverWait(driver, 5)

        self._click_pop_up_ad(wait, driver)

        self._scroll_down_until_page_bottom(driver)

        logger.info('Get the page source after the page has loaded')
        html = driver.page_source

        logger.info('Close the webdriver after obtaining the HTML content')
        driver.quit()

        logger.info('Parse the HTML content with BeautifulSoup')
        soup = bs4.BeautifulSoup(html, 'html.parser')

        hotel_class = 'f6431b446c.a15b38c233'
        price_class = 'f6431b446c.fbfd7c1165.e84eb96b1f'
        review_class = 'a3b8729ab1.d86cee9b25'
        box_class = 'c066246e13'

        self._scrape_data_from_box_class(soup, box_class, hotel_class, price_class, review_class, data)

    @staticmethod
    def _transform_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform scraped hotel data.
        :param df: Pandas dataframe.
        :return: Pandas dataframe.
        """
        logger.info("Transforming data...")

        # Remove duplicate rows from the DataFrame based on 'Hotel' column
        df_filtered = df.drop_duplicates(subset='Hotel')

        # Convert 'Price' and 'Review' columns to numeric using .loc
        df_filtered.loc[:, 'Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df_filtered.loc[:, 'Review'] = pd.to_numeric(df['Review'], errors='coerce')

        # Add a new column for the ratio of Price to Review using .loc
        df_filtered.loc[:, 'Price/Review'] = df_filtered['Price'] / df_filtered['Review']

        # Sort the DataFrame based on the 'Price/Review' column
        return df_filtered.sort_values(by='Price/Review')

    def start_scraping_process(self, check_in: str, check_out: str) -> None | DataFrame:
        """
        Main function to start the web scraping process.
        :param check_in: Check-in date.
        :param check_out: Check-out date.
        :return: None.
                Return a Pandas DataFrame for testing purpose only.
        """
        logger.info(f"Starting web-scraping... Period: {check_in} to {check_out}")

        # Create a DataFrame to store the data
        data = {'Hotel': [], 'Price': [], 'Review': []}

        city = self.details.city
        group_adults = self.details.group_adults
        num_rooms = self.details.num_rooms
        group_children = self.details.group_children
        selected_currency = self.details.selected_currency

        url = (f'https://www.booking.com/searchresults.en-gb.html?ss={city}&checkin'
               f'={check_in}&checkout={check_out}&group_adults={group_adults}'
               f'&no_rooms={num_rooms}&group_children={group_children}'
               f'&selected_currency={selected_currency}&nflt=ht_id%3D204')

        self._scrape(url, data)

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data)

        df['City'] = city

        # Hotel data of the given date
        df['Date'] = check_in

        # Date which the data was collected
        df['AsOf'] = datetime.datetime.now()

        df_filtered = self._transform_data(df)

        migrate_data_to_sqlite(df_filtered)

        return df_filtered


if __name__ == '__main__':
    pass