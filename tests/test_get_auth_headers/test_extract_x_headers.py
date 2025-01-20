from unittest.mock import patch, Mock, mock_open

import pytest
from playwright.sync_api import Page, Browser, BrowserContext

from get_auth_headers import extract_x_headers, handle_request, update_env_example


@pytest.fixture
def mock_playwright():
    with patch('get_auth_headers.sync_playwright') as mock_playwright:
        mock_browser = Mock(spec=Browser)
        mock_page = Mock(spec=Page)
        Mock(spec=BrowserContext)

        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page

        yield mock_playwright, mock_browser, mock_page


def test_extract_x_headers_navigation(mock_playwright):
    _, _, mock_page = mock_playwright

    extract_x_headers()

    # Check if the function navigates to Booking.com
    mock_page.goto.assert_called_once_with("https://www.booking.com")

    # Check if the function fills in the search input and presses Enter
    mock_page.fill.assert_called_once_with('input[name="ss"]', "Tokyo")
    mock_page.press.assert_called_once_with('input[name="ss"]', "Enter")


def test_extract_x_headers_request_interception(mock_playwright):
    _, _, mock_page = mock_playwright

    extract_x_headers()

    # Check if request interception is set up
    mock_page.on.assert_called_once_with("request", handle_request)


@patch('get_auth_headers.update_env_example')
def test_handle_request_graphql(mock_update_env):
    mock_request = Mock()
    mock_request.url = "https://www.booking.com/dml/graphql?query=somequery"
    mock_request.headers = {
        'x-booking-context-action-name': 'searchresults',
        'user-agent': 'Mozilla/5.0',
        'content-type': 'application/json'
    }

    handle_request(mock_request)

    expected_env_vars = {
        'X_BOOKING_CONTEXT_ACTION_NAME': 'searchresults',
        'USER_AGENT': 'Mozilla/5.0'
    }
    mock_update_env.assert_called_once_with(expected_env_vars)


def test_handle_request_non_graphql():
    mock_request = Mock()
    mock_request.url = "https://www.booking.com/some-other-page"

    with patch('get_auth_headers.update_env_example') as mock_update_env:
        handle_request(mock_request)
        mock_update_env.assert_not_called()


@patch('builtins.open', new_callable=mock_open, read_data="X_BOOKING_CONTEXT_ACTION_NAME=\nUSER_AGENT=\n")
@patch('get_auth_headers.ENV_FILENAME', '.env.test')
def test_update_env_example(mock_file):
    env_vars = {
        'X_BOOKING_CONTEXT_ACTION_NAME': 'searchresults',
        'USER_AGENT': 'Mozilla/5.0'
    }

    update_env_example(env_vars)

    # Check that open was called twice (once for reading, once for writing)
    assert mock_file.call_count == 2

    # Check the read operation
    mock_file.assert_any_call('.env.example', 'r')

    # Check the write operation
    mock_file.assert_any_call('.env.test', 'w')

    # Check the content written
    handle = mock_file()
    handle.writelines.assert_called_once_with(['X_BOOKING_CONTEXT_ACTION_NAME=searchresults\n', 'USER_AGENT=Mozilla/5.0\n'])

    # Check that print was called with the correct message
    with patch('builtins.print') as mock_print:
        update_env_example(env_vars)
        mock_print.assert_called_once_with("Headers updated in .env.test file")