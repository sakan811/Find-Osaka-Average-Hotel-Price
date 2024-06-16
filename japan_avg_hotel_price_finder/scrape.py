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
import time

import bs4
import pandas as pd
from pandas import DataFrame
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, WebDriverException, \
    ElementClickInterceptedException, NoSuchWindowException
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
    df_filtered = df.drop_duplicates(subset='Hotel').copy()

    # Convert columns to numeric values
    df_filtered.loc[:, 'Price'] = pd.to_numeric(df_filtered['Price'], errors='coerce')
    df_filtered.loc[:, 'Review'] = pd.to_numeric(df_filtered['Review'], errors='coerce')

    # Calculate the Price/Review ratio
    df_filtered.loc[:, 'Price/Review'] = df_filtered['Price'] / df_filtered['Review']

    # Sort the DataFrame based on the 'Price/Review' column
    return df_filtered.sort_values(by='Price/Review')


def create_df_from_scraped_data(check_in: str, check_out: str, city: str, hotel_data_dict: dict) -> DataFrame:
    """
    Create a DataFrame from the collected data.
    :param check_in: The check-in date.
    :param check_out: The check-out date.
    :param city: City where the hotels are located.
    :param hotel_data_dict: Dictionary with hotel data.
    :returns: Pandas DataFrame with hotel data or None in case 'hotel_data_dict' is None.
    """
    logger.info("Create a DataFrame from the collected data")
    df = pd.DataFrame()
    if hotel_data_dict:
        try:
            df = pd.DataFrame(hotel_data_dict)

            logger.info("Add City column to DataFrame")
            df['City'] = city

            logger.info("Add Date column to DataFrame")
            df['Date'] = check_in

            logger.info("Add AsOf column to DataFrame")
            df['AsOf'] = datetime.datetime.now()

            df = transform_data(df)
        except ValueError:
            logger.error(f'ValueError: Error when creating a DataFrame for {check_in} to {check_out} data')
        return df
    else:
        logger.warning(f'hotel_data_dict is None. Return None.')
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
    except TimeoutException:
        logger.error(f'TimeoutException: {url} failed')
    except NoSuchElementException:
        logger.error(f'NoSuchElementException: {url} failed')
    except WebDriverException:
        logger.error(f'WebDriverException: {url} failed')
    except Exception as e:
        logger.error(e)
        logger.error(f'Unexpected error: {url} failed')


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
        self.obstructing_classes = ['a3f7e233ba', 'f0fbe41bfe.b290b28eaf',
                                    'bf33709ee1.a190bb5f27.c73e91a7c9.bb5314095f.e47e45fccd.a94fe207f7']
        self.num_load_more_result_clicked_list = 0
        self.num_pop_up_clicked_list = 0

    def _click_load_more_result_button(self, wait: WebDriverWait, driver: WebDriver) -> int | None:
        """
        Click 'load more result' button to load more hotels.
        :param wait: Selenium WebDriverWait object.
        :param driver: Selenium WebDriver.
        :return: Number of 'load more result' button clicked or None in case it's not clicked.
        """
        logger.info("Click 'load more result' button.")

        load_more_result_css_selector = ('#bodyconstraint-inner > div:nth-child(8) > div > div.c1cce822c4 > '
                                         'div.b3869ababc > div.b2c588d242 > div.c1b783d372.b99ea5ed8e > '
                                         'div.fb4e9b097f > div.fa298e29e2.a1b24d26fa > button > span')
        try:
            load_more_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, load_more_result_css_selector)))
            load_more_button.click()
        except NoSuchElementException:
            logger.error(f'NoSuchElementException: The \'load more result\' button not found. Keep scrolling.')
        except ElementClickInterceptedException as e:
            logger.error(e)
            logger.error("ElementClickInterceptedException: The pop-up ad is obscured.")
        except TimeoutException:
            logger.error(f'TimeoutException: The \'load more result\' button timed out.')
        except Exception as e:
            logger.error(e)
            logger.error(f'Unexpected error occurred')
        else:
            logger.debug(f'Load more result button clicked successfully')
            return 1

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

    def _scrape(self, url: str) -> None | dict:
        """
        Scrape hotel data from the website.
        :param url: Website URL.
        :return: Dictionary with hotel data or None in case error happened.
        """
        logger.info("Connect to the Selenium Webdriver")
        driver = connect_to_webdriver()
        html = None
        num_pop_up_clicked_list = []
        num_load_more_result_clicked_list = []
        try:
            get_url_with_driver(driver, url)

            wait = WebDriverWait(driver, timeout=0.1, poll_frequency=0)

            num_pop_up_clicked: int = self._click_pop_up_ad(wait, driver)
            if num_pop_up_clicked is not None:
                num_pop_up_clicked_list.append(num_pop_up_clicked)

            num_load_more_result_clicked, num_pop_up_clicked = self._scroll_down_until_page_bottom(wait, driver)
            if num_load_more_result_clicked is not None:
                num_load_more_result_clicked_list.append(num_load_more_result_clicked)
            if num_pop_up_clicked is not None:
                num_pop_up_clicked_list.append(num_pop_up_clicked)

            self.num_pop_up_clicked_list = sum(num_pop_up_clicked_list)
            self.num_load_more_result_clicked_list = sum(num_load_more_result_clicked_list)

            logger.info('Get the page source after the page has loaded')
            html = driver.page_source
        except Exception as e:
            logger.error(e)
            logger.error(f"Unexpected error occurred.")
        finally:
            logger.info('Close the webdriver after obtaining the HTML content or if an error occurs')
            driver.quit()

        logger.info('Parse the HTML content with BeautifulSoup')
        if html is not None:
            soup = bs4.BeautifulSoup(html, 'html.parser')
            return self._find_hotel_data_from_box_class(soup)
        else:
            return None

    def start_scraping_process(self, check_in: str, check_out: str, to_sqlite: bool = False) -> DataFrame:
        """
        Main function to start the web scraping process.
        :param check_in: Check-in date.
        :param check_out: Check-out date.
        :param to_sqlite: If True, save the scraped data to a SQLite database, else save to CSV.
        :return: Pandas DataFrame.
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

        hotel_data_dict: dict | None = self._scrape(url)

        df_filtered = pd.DataFrame()
        if hotel_data_dict:
            df_filtered: pd.DataFrame = create_df_from_scraped_data(check_in, check_out, city, hotel_data_dict)

            if not df_filtered.empty:
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
                    except FileExistsError:
                        # If the directory already exists, log a message and continue
                        logger.error(f'FileExistsError: {save_dir} directory already exists')

                    file_path = os.path.join(save_dir, f'{city}_hotel_data_{check_in}_to_{check_out}.csv')
                    df_filtered.to_csv(file_path, index=False)
        else:
            logger.warning("HTML content is None. No data was scraped.")

        if self.num_load_more_result_clicked_list < 1:
            logger.warning("Load more result button is never clicked. "
                           "The CSS selector for the load more result button might have a problem."
                           "Please update the CSS selector in '_click_load_more_result_button' function.")
        if self.num_pop_up_clicked_list < 1:
            logger.warning("Pop-up ad is never clicked. "
                           "The CSS selector for the pop-up ad might have a problem."
                           "Please update the CSS selector of the pop-up ad in '_click_pop_up_ad' function.")

        logger.info('Finally, return a Pandas DataFrame')
        return df_filtered

    def _click_pop_up_ad(self, wait: WebDriverWait, driver: WebDriver) -> int | None:
        """
        Click pop-up ad.
        :param wait: Selenium WebDriverWait object.
        :param driver: Selenium WebDriver object.
        :return: Number of pop-up ads clicked or None in case it's not clicked.
        """
        logger.info("Clicking pop-up ad...")

        ads_css_selector = ('div.e93d17c51f:nth-child(1) > button:nth-child(1) > span:nth-child(1) > span:nth-child(1) '
                            '> svg:nth-child(1)')

        try:
            ads = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ads_css_selector)))
            ads.click()
        except NoSuchElementException:
            logger.error(f'Pop-up ad not found')
        except TimeoutException:
            logger.error(f'Pop-up ad timed out')
            logger.error(f'Moving on')
        except ElementClickInterceptedException as e:
            logger.error(e)
            logger.error("ElementClickInterceptedException: The pop-up ad is obscured.")
        except Exception as e:
            logger.error(e)
            logger.error(f'Unexpected error occurred')
        else:
            logger.debug('Clicked the pop-up ads successfully')
            return 1

    def _scroll_down_until_page_bottom(self, wait: WebDriverWait, driver: WebDriver) -> tuple[int, int] | None:
        """
        Scroll down and click 'Load more result' button if present.

        Scroll down until reach the bottom of the page.
        :param wait: Selenium WebDriverWait object.
        :param driver: Selenium WebDriver.
        :return: Tuple of the number of clicks on 'Load more result' button and 'pop-up ads'.
                None in case 'load more result' button or pop-up ad is not clicked.
        """
        logger.info("Scrolling down until the bottom of the page...")
        current_height = 0
        new_height = 0
        click_pop_up_ad_clicked_list = []
        load_more_result_button_clicked_list = []
        while True:
            try:
                # Get current height
                current_height = driver.execute_script("return window.scrollY")
                logger.debug(f'{current_height = }')

                # Scroll down to the bottom
                driver.execute_script("window.scrollBy(0, 2000);")

                # Get current height
                new_height = driver.execute_script("return window.scrollY")
                logger.debug(f'{new_height = }')
            except NoSuchWindowException:
                logger.error('No such window: The browsing context has been discarded.')

            # If the new height is the same as the last height, then the bottom is reached
            if current_height == new_height:
                logger.info("Reached the bottom of the page.")
                break

            # Click 'load more result' button if present
            num_load_more_result_button_clicked = self._click_load_more_result_button(wait, driver)
            if num_load_more_result_button_clicked is not None:
                load_more_result_button_clicked_list.append(num_load_more_result_button_clicked)

            logger.info("Clicking pop-up ad in case it appears...")
            num_pop_up_ad_clicked = self._click_pop_up_ad(wait, driver)
            if num_pop_up_ad_clicked is not None:
                click_pop_up_ad_clicked_list.append(num_pop_up_ad_clicked)

            # Update current height
            current_height = new_height

        return sum(load_more_result_button_clicked_list), sum(click_pop_up_ad_clicked_list)


if __name__ == '__main__':
    pass
