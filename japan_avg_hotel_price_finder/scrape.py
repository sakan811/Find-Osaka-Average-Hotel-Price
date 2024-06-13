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
import os
import re

import bs4
import pandas as pd
from pandas import DataFrame
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from japan_avg_hotel_price_finder.configure_logging import configure_logging_with_file
from japan_avg_hotel_price_finder.migrate_to_sqlite import migrate_data_to_sqlite
from set_details import Details

logger = configure_logging_with_file('jp_hotel_data.log', 'jp_hotel_data')


def append_to_hotel_dict(
        hotel_data_dict: dict,
        hotel_element: bs4.ResultSet,
        price_element: bs4.ResultSet,
        review_element: bs4.ResultSet) -> dict:
    """
    Append data to dataframe.
    :param hotel_data_dict: Dictionary to store hotel data.
    :param hotel_element: Hotel data element from the HTML source.
    :param price_element: Price data element from the HTML source.
    :param review_element: Review score data element from the HTML source.
    :return: Dictionary with hotel data added.
    """
    # Check if all elements are presented before extracting data
    if hotel_element and price_element and review_element:
        hotel_name = hotel_element[0].text
        price = re.sub(r'[^0-9]', '', price_element[0].text)
        review_score = review_element[0].text.split()[1]

        if hotel_name and price and review_score:
            hotel_data_dict['Hotel'].append(hotel_name)
            hotel_data_dict['Price'].append(price)
            hotel_data_dict['Review'].append(review_score)
            logger.debug("Appended data to hotel data dictionary successfully")
        else:
            logger.warning('Data extraction did not work properly.')
            logger.debug(f'{hotel_name = }')
            logger.debug(f'{hotel_element = }')
            logger.debug(f'{price = }')
            logger.debug(f'{price_element = }')
            logger.debug(f'{review_score = }')
            logger.debug(f'{review_element = }')
    else:
        logger.warning(f'Not all elements are presented.')

    return hotel_data_dict


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
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


def create_df_from_scraped_data(check_in, check_out, city, hotel_data_dict) -> pd.DataFrame:
    """
    Create a DataFrame from the collected data.
    :param check_in: The check-in date.
    :param check_out: The check-out date.
    :param city: City where the hotels are located.
    :param hotel_data_dict: Dictionary with hotel data.
    :returns: Pandas DataFrame with hotel data
    """
    logger.info("Create a DataFrame from the collected data")
    df = None
    try:
        df = pd.DataFrame(hotel_data_dict)

        logger.info("Add City column to DataFrame")
        df['City'] = city

        logger.info("Add Date column to DataFrame")
        df['Date'] = check_in

        logger.info("Add AsOf column to DataFrame")
        df['AsOf'] = datetime.datetime.now()

        df = transform_data(df)
    except ValueError as e:
        logger.error(e)
        logger.error(f'Error when creating a DataFrame for {check_in} to {check_out} data')
    return df


def get_url_with_driver(driver: WebDriver, url: str) -> None:
    """
    Get the URL with Selenium WebDriver.
    :param driver: Selenium WebDriver
    :param url: The target URL.
    :return: None
    """
    logger.info(f"Get the URL: {url}")
    try:
        driver.get(url)
    except TimeoutException as e:
        logger.error(f'TimeoutException: {url} failed due to {e}')
    except NoSuchElementException as e:
        logger.error(f'NoSuchElementException: {url} failed due to {e}')
    except WebDriverException as e:
        logger.error(f'WebDriverException: {url} failed due to {e}')
    except Exception as e:
        logger.error(e)
        logger.error(f'{url} failed due to {e}')


def connect_to_webdriver() -> WebDriver:
    """
    Connect to the Selenium WebDriver.
    :return: Selenium WebDriver
    """
    # Configure driver options
    options = webdriver.FirefoxOptions()
    # Block image loading
    options.set_preference('permissions.default.stylesheet', 2)
    options.set_preference('permissions.default.image', 2)
    options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    options.add_argument("--headless")
    # Disable blink features related to automation control
    options.add_argument('--disable-blink-features=AutomationControlled')
    # Initialize the driver with the configured options
    driver = webdriver.Firefox(options=options)
    return driver


class BasicScraper:
    def __init__(self, details: Details):
        """
        Initialize the Scraper class with the following parameter:
        :param  details: Details dataclass object
        """
        self.details = details
        self.hotel_class = 'fa4a3a8221.b121bc708f'
        self.price_class = 'fa4a3a8221.b22052b420.f53c51ec80'
        self.review_class = 'f13857cc8c.e008572b71'
        self.box_class = 'fa298e29e2.b74446e476.e40c0c68b1.ea1d0cfcb7.d8991ab7ae.e8b7755ec7.ad0e783e41'
        self.hotel_data_dict = {'Hotel': [], 'Price': [], 'Review': []}
        self.load_more_result_clicked = 0
        self.pop_up_clicked = 0

    def _click_load_more_result_button(self, driver: WebDriver) -> None:
        """
        Click 'load more result' button to load more hotels.
        :param driver: Selenium WebDriver.
        :return: None
        """
        logger.info("Click 'load more result' button.")

        load_more_result_css_selector = ('#bodyconstraint-inner > div:nth-child(8) > div > div.c1cce822c4 > '
                                         'div.b3869ababc > div.b2c588d242 > div.c1b783d372.b99ea5ed8e > '
                                         'div.fb4e9b097f > div.fa298e29e2.a1b24d26fa > button')

        try:
            wait = WebDriverWait(driver, 2)
            load_more_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, load_more_result_css_selector)))
            load_more_button.click()
        except NoSuchElementException as e:
            logger.error(e)
            logger.error(f'{load_more_result_css_selector} not found. Keep scrolling.')
        except Exception as e:
            logger.error(e)
            logger.error(f'{load_more_result_css_selector} failed due to {e}')
        else:
            self.load_more_result_clicked += 1
            logger.debug(f'{load_more_result_css_selector} clicked successfully')

    def _find_box_elements(self, soup) -> bs4.ResultSet:
        """
        Find box elements from box class.
        :param soup: bs4.BeautifulSoup object.
        :return: bs4.ResultSet
        """
        logger.info("Find the box elements")
        box_elements = soup.select(f'.{self.box_class}')
        return box_elements

    def _find_hotel_data_from_box_class(self, soup: bs4.BeautifulSoup) -> dict:
        """
        Find hotel data from box class.
        :param soup: bs4.BeautifulSoup object.
        :return: Dictionary with hotel data.
        """
        logger.info("Finding hotel data from box class...")

        box_elements: bs4.ResultSet = self._find_box_elements(soup)
        if len(box_elements) == 0:
            logger.error(f'{self.box_class} not found')
            raise Exception(f'{self.box_class} not found')

        hotel_data_dict = self.hotel_data_dict

        hotel_data_dict = self._find_data_in_box_elements(box_elements, hotel_data_dict)

        return hotel_data_dict

    def _find_data_in_box_elements(self, box_elements: bs4.ResultSet, hotel_data_dict: dict) -> dict:
        """
        Find data in box elements.
        :param box_elements: Box elements.
        :param hotel_data_dict: Dictionary storing hotel data.
        :return: Dictionary with hotel data.
        """
        logger.info("Finding the elements within the box element...")
        for box_element in box_elements:
            hotel_element = box_element.select(f'.{self.hotel_class}')
            price_element = box_element.select(f'.{self.price_class}')
            review_element = box_element.select(f'.{self.review_class}')

            logger.debug("Append data to hotel data dictionary")
            hotel_data_dict = append_to_hotel_dict(hotel_data_dict, hotel_element, price_element, review_element)
        return hotel_data_dict

    def _scrape(self, url: str) -> dict:
        """
        Scrape hotel data from the website.
        :param url: Website URL.
        :return: Dictionary with hotel data.
        """
        logger.info("Connect to the Selenium Webdriver")
        driver = connect_to_webdriver()

        get_url_with_driver(driver, url)

        wait = WebDriverWait(driver, 2)

        self._click_pop_up_ad(wait)

        self._scroll_down_until_page_bottom(driver)

        if self.pop_up_clicked < 1:
            logger.warning("Pop-up ad is never clicked")

        if self.load_more_result_clicked < 1:
            logger.warning("Load more result button is never clicked")
            raise Exception("Load more result button is never clicked."
                            "Check the path to 'load more result button' "
                            "in 'self._click_load_more_result_button' function")

        logger.info('Get the page source after the page has loaded')
        html = driver.page_source

        logger.info('Close the webdriver after obtaining the HTML content')
        driver.quit()

        logger.info('Parse the HTML content with BeautifulSoup')
        soup = bs4.BeautifulSoup(html, 'html.parser')

        return self._find_hotel_data_from_box_class(soup)

    def start_scraping_process(self, check_in: str, check_out: str, to_sqlite: bool = False) -> None | DataFrame:
        """
        Main function to start the web scraping process.
        :param check_in: Check-in date.
        :param check_out: Check-out date.
        :param to_sqlite: If True, save the scraped data to a SQLite database, else save to CSV.
        :return: None or Pandas DataFrame.
        """
        logger.info(f"Starting web-scraping... Period: {check_in} to {check_out}")

        city = self.details.city
        group_adults = self.details.group_adults
        num_rooms = self.details.num_rooms
        group_children = self.details.group_children
        selected_currency = self.details.selected_currency

        url = (f'https://www.booking.com/searchresults.en-gb.html?ss={city}&checkin'
               f'={check_in}&checkout={check_out}&group_adults={group_adults}'
               f'&no_rooms={num_rooms}&group_children={group_children}'
               f'&selected_currency={selected_currency}&nflt=ht_id%3D204')

        hotel_data_dict = self._scrape(url)

        df_filtered = create_df_from_scraped_data(check_in, check_out, city, hotel_data_dict)

        if df_filtered is not None:
            if to_sqlite:
                logger.info('Save data to SQLite database')
                migrate_data_to_sqlite(df_filtered, self.details)
            else:
                logger.info('Save data to CSV')
                save_dir = 'scraped_hotel_data_csv'

                try:
                    # Attempt to create the directory
                    os.makedirs(save_dir)
                    logger.info(f'Created {save_dir} directory')
                except FileExistsError as e:
                    # If the directory already exists, log a message and continue
                    logger.error(e)
                    logger.error(f'{save_dir} directory already exists')

                file_path = os.path.join(save_dir, f'{city}_hotel_data_{check_in}_to_{check_out}.csv')
                df_filtered.to_csv(file_path, index=False)

        logger.info('Return data as DataFrame')
        return df_filtered

    def _click_pop_up_ad(self, wait: WebDriverWait) -> None:
        """
        Click pop-up ad.
        :param wait: Selenium WebDriverWait object.
        :return: None.
        """
        logger.info("Clicking pop-up ad...")

        ads_css_selector = '.f4552b6561 > span:nth-child(1) > span:nth-child(1) > svg:nth-child(1)'

        try:
            ads = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ads_css_selector)))
            ads.click()
        except NoSuchElementException as e:
            logger.error(e)
            logger.error(f'{ads_css_selector} not found')
        except TimeoutException as e:
            logger.error(e)
            logger.error(f'{ads_css_selector} timed out')
            logger.error(f'Moving on')
        except Exception as e:
            logger.error(e)
            logger.error(f'{ads_css_selector} failed due to {e}')
        else:
            self.pop_up_clicked += 1
            logger.debug('Clicked the pop-up ads successfully')

    def _scroll_down_until_page_bottom(self, driver: WebDriver) -> None:
        """
        Scroll down and click 'Load more result' button if present.

        Scroll down until reach the bottom of the page.
        :param driver: Selenium WebDriver.
        :return: None.
        """
        logger.info("Scrolling down until the bottom of the page...")

        while True:
            current_height = driver.execute_script("return window.scrollY")
            logger.debug(f'{current_height = }')

            # Scroll down to the bottom
            driver.execute_script("window.scrollBy(0, 2000);")

            # Get current height
            new_height = driver.execute_script("return window.scrollY")
            logger.debug(f'{new_height = }')

            # If the new height is the same as the last height, then the bottom is reached
            if current_height == new_height:
                logger.info("Reached the bottom of the page.")
                break

            # Click 'load more result' button if present
            self._click_load_more_result_button(driver)

            wait = WebDriverWait(driver, 2)
            logger.info("Clicking pop-up ad in case it appears...")
            self._click_pop_up_ad(wait)


if __name__ == '__main__':
    pass
