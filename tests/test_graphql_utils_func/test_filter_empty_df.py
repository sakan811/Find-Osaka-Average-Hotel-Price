import pandas as pd

from japan_avg_hotel_price_finder.graphql_scraper_func.graphql_utils_func import filter_empty_df


def test_filter_empty_df():
    # Create sample DataFrames
    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame()
    df3 = pd.DataFrame({'C': [5, 6]})

    # Test with mix of empty and non-empty DataFrames
    input_list = [df1, df2, df3]
    result = filter_empty_df(input_list)
    assert len(result) == 2
    assert all(not df.empty for df in result)

    # Test with all non-empty DataFrames
    all_non_empty = [df1, df3]
    assert filter_empty_df(all_non_empty) == all_non_empty

    # Test with all empty DataFrames
    all_empty = [pd.DataFrame(), pd.DataFrame()]
    assert filter_empty_df(all_empty) == []

    # Test with an empty list
    assert filter_empty_df([]) == []

    # Test that function doesn't modify the original list
    original_list = [df1, df2, df3]
    filter_empty_df(original_list)
    assert len(original_list) == 3