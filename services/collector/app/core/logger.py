# services/collector/app/core/logger.py
# logs are being saved in the file collector.log in the root of the project,
# you can change this by changing the filename in basicConfig

import logging


def setup_logger(name: str) -> logging.Logger:
    """Create and configure a logger instance with standardized formatting.

    Initializes the logging system with INFO level and a consistent format
    that includes timestamps, log level, logger name, and message content.
    Configures basicConfig once and returns a named logger for the specified module.

    Args:
        name (str): The name of the logger, typically the module name (__name__).
            This is used to identify log messages and enable per-module filtering.

    Returns:
        logging.Logger: A configured logger instance ready for use in the module.

    Example:
        logger = setup_logger(__name__)
        logger.info("Connection established")
    """
    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s | " "%(levelname)s | " "%(name)s | " "%(message)s"),
    )

    return logging.getLogger(name)
