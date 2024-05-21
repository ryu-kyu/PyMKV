import logging
import os
import sys
import shutil

import pymkv.constants as constants


OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), constants.OUTPUT_DIR_NAME
)


def remove_output_dir() -> None:
    """
    Removes output directory, if exists.
    """
    if not os.path.exists(OUTPUT_DIR):
        return
    shutil.rmtree(OUTPUT_DIR)


class PyMkvLogger:
    """
    PyMKV Logger

    Each Python module uses its own logger instance to:
        - write to same log file located in 'OUTPUT_DIR'
        - print log to stdout
    """
    logger = logging.Logger = None

    def __init__(self, logger_name: str) -> None:
        """
        Create logging instance
        :param logger_name: Logger name, typically filename
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        if not os.path.exists(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)

        self.attach_handlers()

    def attach_handlers(self) -> None:
        """
        Attaches file handler and stdout handlers to logger
        """
        console_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler(os.path.join(str(OUTPUT_DIR), constants.LOG_FILE_NAME))
        log_formatter = logging.Formatter(
            "%s(levelname)s %(name)s %(asctime)s %(message)s"
        )

        file_handler.setFormatter(log_formatter)
        console_handler.setFormatter(log_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
