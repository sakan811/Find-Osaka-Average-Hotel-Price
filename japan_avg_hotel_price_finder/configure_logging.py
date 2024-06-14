import concurrent.futures
import logging


class AsyncFileHandler(logging.Handler):
    def __init__(self, filename, mode='a'):
        super().__init__()
        self.filename = filename
        self.mode = mode
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.queue = []

    def emit(self, record):
        log_entry = self.format(record)
        self.queue.append(log_entry)
        self.executor.submit(self._write_log)

    def _write_log(self):
        if self.queue:
            with open(self.filename, self.mode) as log_file:
                while self.queue:
                    log_file.write(self.queue.pop(0) + '\n')

    def close(self):
        self.executor.shutdown(wait=True)
        super().close()


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

    # Create an AsyncFileHandler to write logs to the specified file
    # 'w' for write mode (overwrite)
    async_file_handler = AsyncFileHandler(log_file, mode='w')

    # Create a StreamHandler to output logs to the terminal
    stream_handler = logging.StreamHandler()

    # Create a Formatter with the custom log format
    formatter = logging.Formatter(log_format)

    # Set the Formatter for both the FileHandler and StreamHandler
    async_file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add both the FileHandler and StreamHandler to the root logger
    logger.addHandler(async_file_handler)
    logger.addHandler(stream_handler)

    return logger
