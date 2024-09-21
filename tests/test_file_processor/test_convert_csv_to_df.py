from japan_avg_hotel_price_finder.file_processor.file_processor import find_csv_files, convert_csv_to_df


def test_convert_csv_to_df():
    directory = 'tests/test_file_processor/test_find_csv_files'
    csv_files = find_csv_files(directory)
    df = convert_csv_to_df(csv_files)
    assert not df.empty


def test_convert_csv_to_df_empty():
    directory_2 = 'tests/test_file_processor/test_find_csv_files_2'
    csv_files = find_csv_files(directory_2)
    df = convert_csv_to_df(csv_files)
    assert df is None