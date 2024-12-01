from unittest.mock import patch, mock_open

import pytest

from get_auth_headers import update_env_example


@pytest.fixture
def mock_env_file():
    return "X_BOOKING_CONTEXT_ACTION_NAME=\nUSER_AGENT=\n"


@pytest.mark.parametrize('env_filename', ['.env.test'])
def test_update_env_example(mock_env_file, env_filename):
    with patch('builtins.open', mock_open(read_data=mock_env_file)) as mock_file, \
            patch('get_auth_headers.ENV_FILENAME', env_filename):
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
        mock_file.assert_any_call(env_filename, 'w')

        # Check the content written
        handle = mock_file()
        handle.writelines.assert_called_once_with([
            'X_BOOKING_CONTEXT_ACTION_NAME=searchresults\n',
            'USER_AGENT=Mozilla/5.0\n'
        ])


def test_update_env_example_partial_update():
    mock_file_content = "X_HEADER=old_value\nOTHER_HEADER=keep_this\n"
    with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file, \
            patch('get_auth_headers.ENV_FILENAME', '.env.test'):
        env_vars = {
            'X_HEADER': 'new_value'
        }

        update_env_example(env_vars)

        handle = mock_file()
        handle.writelines.assert_called_once_with([
            'X_HEADER=new_value\n',
            'OTHER_HEADER=keep_this\n'
        ])


def test_update_env_example_empty_file():
    with patch('builtins.open', mock_open(read_data="")) as mock_file, \
            patch('get_auth_headers.ENV_FILENAME', '.env.test'):
        env_vars = {
            'NEW_HEADER': 'new_value'
        }

        update_env_example(env_vars)

        handle = mock_file()
        handle.writelines.assert_called_once_with([])


def test_update_env_example_print_message(capsys):
    with patch('builtins.open', mock_open(read_data="")), \
            patch('get_auth_headers.ENV_FILENAME', '.env.test'):
        update_env_example({})

        captured = capsys.readouterr()
        assert captured.out == "Headers updated in .env.test file\n"
