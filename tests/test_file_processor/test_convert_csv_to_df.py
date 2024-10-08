from unittest.mock import patch

import pandas as pd

from japan_avg_hotel_price_finder.file_processor.file_processor import convert_csv_to_df


@patch('pandas.read_csv')
@patch('pandas.concat')
def test_convert_csv_to_df(mock_concat, mock_read_csv):
    # Mock csv files
    csv_files = ['file1.csv', 'file2.csv']

    # Mock pd.read_csv to return a DataFrame for each file
    mock_read_csv.side_effect = [
        pd.DataFrame({'A': [1, 2], 'B': [3, 4]}),
        pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
    ]

    # Mock pd.concat to return a concatenated DataFrame
    mock_concat.return_value = pd.DataFrame({'A': [1, 2, 5, 6], 'B': [3, 4, 7, 8]})

    # Call the function
    result = convert_csv_to_df(csv_files)

    # Assertions
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4  # Combined length of both DataFrames
    assert list(result.columns) == ['A', 'B']

    # Verify that read_csv and concat were called
    assert mock_read_csv.call_count == 2
    mock_concat.assert_called_once()


@patch('pandas.read_csv')
def test_convert_csv_to_df_empty(mock_read_csv):
    # Mock empty list of csv files
    csv_files = []

    # Call the function
    result = convert_csv_to_df(csv_files)

    # Assertions
    assert result is None

    # Verify that read_csv was not called
    mock_read_csv.assert_not_called()