from japan_avg_hotel_price_finder.file_processor.file_processor import find_csv_files


def test_find_csv_files():
    directory = 'tests/test_utils/test_find_csv_files'
    csv_files = find_csv_files(directory)
    print(csv_files)
    assert len(csv_files) > 0


def test_find_csv_files_empty():
    directory_2 = 'tests/test_utils/test_find_csv_files_2'
    csv_files = find_csv_files(directory_2)
    assert len(csv_files) == 0
