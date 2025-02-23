import pandas as pd
import numpy as np

from japan_avg_hotel_price_finder.configure_logging import main_logger


def extract_hotel_data(df_list: list[pd.DataFrame], hotel_data_list: list[dict]) -> None:
    """
    Extract data from a list of hotel data.
    :param df_list: A list to store Pandas Dataframes.
    :param hotel_data_list: List of results.
    :return:
    """
    main_logger.debug("Extracting data...")
    if hotel_data_list:
        for hotel_data in hotel_data_list:
            main_logger.debug("Initialize lists to store extracted data")
            display_names = []
            review_scores = []
            final_prices = []
            location = []
            for key, val in hotel_data.items():
                if key == "displayName":
                    if val and 'text' in val:
                        display_names.append(val['text'])
                    else:
                        display_names.append(None)

                if key == "basicPropertyData":
                    if val and 'reviewScore' in val and 'score' in val['reviewScore']:
                        review_scores.append(float(val['reviewScore']['score']))
                    else:
                        review_scores.append(np.nan)

                if key == "blocks":
                    if val and val[0] and 'finalPrice' in val[0] and 'amount' in val[0]['finalPrice']:
                        final_prices.append(float(val[0]['finalPrice']['amount']))
                    else:
                        final_prices.append(np.nan)

                if key == "location":
                    if val and 'displayLocation' in val:
                        location.append(val['displayLocation'])
                    else:
                        location.append(None)

            main_logger.debug("Create a Pandas Dataframe to store extracted data")
            df = pd.DataFrame({
                "Hotel": pd.Series(display_names, dtype='object'),
                "Review": pd.Series(review_scores, dtype='float64'),
                "Price": pd.Series(final_prices, dtype='float64'),
                "Location": pd.Series(location, dtype='object')
            })

            main_logger.debug("Append dataframe to a df_list")
            df_list.append(df)
    else:
        main_logger.warning("No hotel data was found.")

