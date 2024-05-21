import argparse
from typing import List

import pymkv.logger as logger


def parse_args(args: List[str] = None) -> argparse.Namespace:
    """
    Parse arguments through argparse
    :param args: List of arguments
    :return: Parsed arguments
    """
    arg_parser = argparse.ArgumentParser(
        description="Utility tool to parse, edit, re-compile MKV files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    arg_parser.add_argument(
        "--rename-all",
        help="Rename all files in batch",
        action="store_true",
        required=False,
        default=False
    )
    arg_parser.add_argument(
        "--input-dir",
        help="Path to directory containing MKV file(s)",
        required=True,
        type=argparse.FileType("r")
    )
    arg_parser.add_argument(
        "--new-filenames",
        help="Path to file containing new filenames to rename to",
        required=False,
        type=argparse.FileType("r")
    )

    return arg_parser.parse_args(args)


def run(args: List[str] = None) -> None:
    """
    Run entry-point runner to execute program
    :param args: List of arguments
    """
    parsed_args = parse_args(args)

    LOGGER = logger.PyMkvLogger(__file__).logger


if __name__ == "__main__":
    run()
