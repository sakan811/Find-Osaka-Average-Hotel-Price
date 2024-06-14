import logging


def configure_logging(logger_name='root') -> None | logging.Logger:
    """
    Configure logging message in terminal.
    :param logger_name: Logger name.
                        Default is 'root'.
    :return: None or logger.
    """
    # Get the root logger
    logger = logging.getLogger(logger_name)

    if logger.hasHandlers():
        logger.handlers.clear()

    # Set the logging level
    logger.setLevel(logging.DEBUG)

    # Define a custom log format
    log_format = '%(asctime)s | %(filename)s | line:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s'

    # Create a StreamHandler (which outputs to the terminal)
    stream_handler = logging.StreamHandler()

    # Create a Formatter with the custom log format
    formatter = logging.Formatter(log_format)

    # Set the Formatter for the StreamHandler
    stream_handler.setFormatter(formatter)

    # Add the StreamHandler to the root logger
    logger.addHandler(stream_handler)

    return logger


def configure_logging_with_file(log_file, logger_name='root') -> None | logging.Logger:
    """
    Configure logging with a file.
    :param log_file: Log file name.
    :param logger_name: Logger name.
                        Default is 'root'.
    :return: None or logger.
    """
    # Get the root logger
    logger = logging.getLogger(logger_name)

    if logger.hasHandlers():
        logger.handlers.clear()

    # Set the logging level
    logger.setLevel(logging.DEBUG)

    # Define a custom log format
    log_format = '%(asctime)s | %(filename)s | line:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s'

    # Create a FileHandler to write logs to the specified file in overwrite mode
    file_handler = logging.FileHandler(log_file, mode='w')  # 'w' for write mode (overwrite)

    # Create a StreamHandler to output logs to the terminal
    stream_handler = logging.StreamHandler()

    # Create a Formatter with the custom log format
    formatter = logging.Formatter(log_format)

    # Set the Formatter for both the FileHandler and StreamHandler
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add both the FileHandler and StreamHandler to the root logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
