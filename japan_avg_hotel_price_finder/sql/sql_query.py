def get_count_of_date_by_mth_asof_today_query():
    """
    Return SQLite query to count distinct dates for each month from the HotelPrice table,
    where the AsOf date is today, UTC Time.
    :returns: SQLite query.
    """
    query = '''
        SELECT strftime('%Y-%m', Date) AS Month, count(distinct Date) AS DistinctDateCount, date(AsOf) AS AsOfDate
        FROM HotelPrice
        WHERE AsOf LIKE date('now') || '%' and City = ?
        GROUP BY Month;
        '''
    return query


def get_dates_of_each_month_asof_today_query():
    """
    Query dates of the given month, where the AsOf is today, UTC Time.
    returns: SQLite query.
    """
    query = '''
            SELECT strftime('%Y-%m-%d', Date) AS Date, date(AsOf) AS AsOfDate
            FROM HotelPrice
            WHERE AsOf LIKE date('now') || '%' and Date BETWEEN ? AND ? and City = ?
            GROUP BY Date;
            '''
    return query