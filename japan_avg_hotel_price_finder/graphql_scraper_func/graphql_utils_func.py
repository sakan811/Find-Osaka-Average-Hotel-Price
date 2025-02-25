import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import main_logger


def concat_df_list(df_list: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatenate a list of Pandas Dataframes.
    :param df_list: A list of Pandas Dataframes.
    :return: Pandas DataFrame.
    """
    main_logger.info("Concatenate a list of Pandas Dataframes")
    if df_list:
        df_list = filter_empty_df(df_list)
        if not df_list:
            return pd.DataFrame()
        # Ensure all DataFrames have the same columns
        columns = df_list[0].columns
        df_list = [df[columns] for df in df_list]
        df_main = pd.concat(df_list, ignore_index=True, join='inner')
        return df_main
    else:
        main_logger.warning("No data was scraped.")
        return pd.DataFrame()


def filter_empty_df(df_list: list[pd.DataFrame]) -> list[pd.DataFrame]:
    """
    Filter out empty DataFrames from a list of DataFrames.
    :param df_list: A list of pandas DataFrames, potentially containing empty DataFrames.
    :return: A new list containing only the non-empty DataFrames from the input list.
    """
    df_list = [df for df in df_list if not df.empty]
    return df_list

