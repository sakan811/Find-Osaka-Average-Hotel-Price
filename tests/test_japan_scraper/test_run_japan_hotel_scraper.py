import pytest
from unittest import TestCase
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine
from datetime import datetime
import argparse
import tempfile
import os

from japan_avg_hotel_price_finder.japan_hotel_scraper import JapanScraper


class TestJapanHotelScraper(TestCase):
    """Test cases for JapanHotelScraper functionality"""

    @classmethod
    def setUpClass(cls):
        """Set up test class - runs once before all tests"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, 'test_japan_scraper.db')
        cls.current_month = datetime.now().month
        cls.current_year = datetime.now().year

    def setUp(self):
        """Set up each test - runs before each test method"""
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        
        # Set up default args
        self.args = argparse.Namespace(
            prefecture=None,
            start_month=self.current_month,
            end_month=self.current_month,
            selected_currency=None,
            start_day=1,
            nights=1,
            scrape_only_hotel=True,
            group_adults=1,
            num_rooms=1,
            group_children=0,
            country='Japan'
        )
        
        # Start the patcher
        self.scraper_patcher = patch('japan_avg_hotel_price_finder.japan_hotel_scraper.JapanScraper')
        self.mock_scraper_class = self.scraper_patcher.start()
        
        # Set up the mock instance
        self.mock_instance = self.mock_scraper_class.return_value
        self.mock_instance.scrape_japan_hotels = AsyncMock()

    def tearDown(self):
        """Clean up after each test - runs after each test method"""
        self.scraper_patcher.stop()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests - runs once after all tests"""
        if os.path.exists(cls.temp_dir):
            os.rmdir(cls.temp_dir)

    def create_scraper(self, **kwargs):
        """Helper method to create a scraper instance with default or custom values"""
        default_args = {
            'city': '',
            'year': self.current_year,
            'month': self.current_month,
            'start_day': 1,
            'nights': 1,
            'scrape_only_hotel': True,
            'selected_currency': 'USD',
            'group_adults': 1,
            'num_rooms': 1,
            'group_children': 0,
            'check_in': '',
            'check_out': '',
            'country': 'Japan',
            'engine': self.engine,
            'start_month': self.current_month,
            'end_month': self.current_month
        }
        default_args.update(kwargs)
        return JapanScraper(**default_args)

    def verify_scraper_args(self, args, expected_values):
        """Helper method to verify scraper arguments"""
        for key, value in expected_values.items():
            self.assertEqual(args[key], value, f"Mismatch in {key}: expected {value}, got {args[key]}")

    @pytest.mark.asyncio
    async def test_default_values(self):
        """Test scraper initialization with default values"""
        # Create scraper with default values
        scraper = self.create_scraper()
        self.mock_scraper_class.return_value = scraper
        
        # Run the scraper
        await scraper.scrape_japan_hotels()
        
        # Verify the scraper was created with correct arguments
        self.mock_scraper_class.assert_called_once()
        args = self.mock_scraper_class.call_args[1]
        
        # Verify all default values
        expected_values = {
            'city': '',
            'year': self.current_year,
            'start_month': self.current_month,
            'end_month': self.current_month,
            'selected_currency': 'USD',
            'start_day': 1,
            'nights': 1,
            'scrape_only_hotel': True,
            'group_adults': 1,
            'num_rooms': 1,
            'group_children': 0,
            'country': 'Japan',
            'check_in': '',
            'check_out': '',
            'engine': self.engine
        }
        self.verify_scraper_args(args, expected_values)

    @pytest.mark.asyncio
    async def test_custom_values(self):
        """Test scraper initialization with custom values"""
        # Create scraper with custom values
        custom_values = {
            'city': 'Tokyo,Osaka',
            'selected_currency': 'JPY',
            'group_adults': 2,
            'num_rooms': 2,
            'group_children': 1,
            'start_month': 1,
            'end_month': 12,
            'start_day': 15,
            'nights': 3
        }
        scraper = self.create_scraper(**custom_values)
        self.mock_scraper_class.return_value = scraper
        
        # Run the scraper
        await scraper.scrape_japan_hotels()
        
        # Verify the scraper was created with correct arguments
        self.mock_scraper_class.assert_called_once()
        args = self.mock_scraper_class.call_args[1]
        
        # Verify custom values while keeping default values for unspecified parameters
        expected_values = {
            'city': 'Tokyo,Osaka',
            'year': self.current_year,
            'start_month': 1,
            'end_month': 12,
            'selected_currency': 'JPY',
            'start_day': 15,
            'nights': 3,
            'scrape_only_hotel': True,
            'group_adults': 2,
            'num_rooms': 2,
            'group_children': 1,
            'country': 'Japan',
            'check_in': '',
            'check_out': '',
            'engine': self.engine
        }
        self.verify_scraper_args(args, expected_values) 