import os

import pandas as pd

from japan_avg_hotel_price_finder.configure_logging import main_logger


def find_csv_files(directory) -> list:
    """
    Find CSV files in the given directory.
    :param directory: Directory to find CSV files.
    :returns: List of CSV files.
    """
    csv_files = []

    main_logger.info("Find all .csv files in the directory and its subdirectories")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                main_logger.debug(f'Found CSV file: {file}')
                csv_files.append(os.path.join(root, file))

    return csv_files


def convert_csv_to_df(csv_files: list) -> pd.DataFrame:
    """
    Convert CSV files to Pandas DataFrame.
    :param csv_files: List of CSV files.
    :returns: Pandas DataFrame.
    """
    main_logger.info("Converting CSV files to Pandas DataFrame...")
    df_list = []
    for csv_file in csv_files:
        main_logger.info(f'Convert CSV: {csv_file} to DataFrame.')
        df = pd.read_csv(csv_file)
        if not df.empty:
            df_list.append(df)

    if df_list:
        # Ensure all DataFrames have the same columns
        columns = df_list[0].columns
        df_list = [df[columns] for df in df_list]
        return pd.concat(df_list, ignore_index=True, join='inner')
    return pd.DataFrame()