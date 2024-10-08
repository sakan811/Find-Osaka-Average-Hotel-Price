import os
from unittest.mock import patch

from japan_avg_hotel_price_finder.file_processor.file_processor import find_csv_files


@patch('os.walk')
def test_find_csv_files(mock_walk):
    # Mock directory structure
    mock_walk.return_value = [
        ('root', ['dir1'], ['file1.csv', 'file2.txt']),
        (os.path.join('root', 'dir1'), [], ['file3.csv', 'file4.csv'])
    ]

    # Call the function
    csv_files = find_csv_files('root')

    # Assertions
    assert len(csv_files) == 3
    expected_files = [
        os.path.join('root', 'file1.csv'),
        os.path.join('root', 'dir1', 'file3.csv'),
        os.path.join('root', 'dir1', 'file4.csv')
    ]
    assert set(csv_files) == set(expected_files)
    assert os.path.join('root', 'file2.txt') not in csv_files

    # Verify that os.walk was called
    mock_walk.assert_called_once_with('root')

@patch('os.walk')
def test_find_csv_files_empty(mock_walk):
    # Mock empty directory structure
    mock_walk.return_value = [
        ('root', [], ['file1.txt', 'file2.png'])
    ]

    # Call the function
    csv_files = find_csv_files('root')

    # Assertions
    assert len(csv_files) == 0

    # Verify that os.walk was called
    mock_walk.assert_called_once_with('root')