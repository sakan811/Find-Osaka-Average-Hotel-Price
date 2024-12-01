from unittest.mock import Mock, patch

import pytest
from playwright.sync_api import Request

from get_auth_headers import handle_request


@pytest.fixture
def mock_request():
    request = Mock(spec=Request)
    request.url = "https://www.booking.com/dml/graphql?query=somequery"
    request.headers = {
        'x-booking-context-action-name': 'searchresults',
        'user-agent': 'Mozilla/5.0',
        'content-type': 'application/json'
    }
    return request

def test_handle_request_graphql(mock_request):
    with patch('get_auth_headers.update_env_example') as mock_update_env:
        handle_request(mock_request)

        expected_env_vars = {
            'X_BOOKING_CONTEXT_ACTION_NAME': 'searchresults',
            'USER_AGENT': 'Mozilla/5.0'
        }
        mock_update_env.assert_called_once_with(expected_env_vars)

def test_handle_request_non_graphql():
    non_graphql_request = Mock(spec=Request)
    non_graphql_request.url = "https://www.booking.com/some-other-page"

    with patch('get_auth_headers.update_env_example') as mock_update_env:
        handle_request(non_graphql_request)
        mock_update_env.assert_not_called()

def test_handle_request_intercept_once():
    with patch('get_auth_headers.update_env_example') as mock_update_env:
        request1 = Mock(spec=Request)
        request1.url = "https://www.booking.com/dml/graphql?query=somequery"
        request1.headers = {'x-test': 'value1'}

        request2 = Mock(spec=Request)
        request2.url = "https://www.booking.com/dml/graphql?query=anotherquery"
        request2.headers = {'x-test': 'value2'}

        handle_request(request1)
        handle_request(request2)

        mock_update_env.assert_called_once()

def test_handle_request_extracts_correct_headers():
    request = Mock(spec=Request)
    request.url = "https://www.booking.com/dml/graphql?query=somequery"
    request.headers = {
        'x-test1': 'value1',
        'x-test2': 'value2',
        'user-agent': 'TestAgent',
        'content-type': 'application/json'
    }

    with patch('get_auth_headers.update_env_example') as mock_update_env:
        handle_request(request)

        expected_env_vars = {
            'X_TEST1': 'value1',
            'X_TEST2': 'value2',
            'USER_AGENT': 'TestAgent'
        }
        mock_update_env.assert_called_once_with(expected_env_vars)

@pytest.fixture(autouse=True)
def reset_intercepted():
    import get_auth_headers
    get_auth_headers.intercepted = False
    yield
    get_auth_headers.intercepted = False