import argparse
import os
import json
import subprocess
import ffmpeg

from pathlib import Path
from typing import List

from PyMKV.logger import PyMkvLogger

LOGGER = PyMkvLogger(__file__).logger


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
        type=str
    )
    arg_parser.add_argument(
        "--new-filenames",
        help="Path to file containing new filenames to rename to",
        required=False,
        type=argparse.FileType("r")
    )
    arg_parser.epilog = """Example:

    # after setting $INPUT_DIR to be where mkv/video files are stored
    poetry run python PyMKV/pymkv_runner.py --input-dir $INPUT_DIR
    """

    return arg_parser.parse_args(args)


def run(args: List[str] = None) -> None:
    """
    Run entry-point runner to execute program
    :param args: List of arguments
    """
    parsed_args = parse_args(args)

    ffmpeg_install_retcode = subprocess.run(
        ["ffmpeg", "-h"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    ).returncode
    if ffmpeg_install_retcode != 0:
        LOGGER.error(
            "'ffmpeg' is not installed. Install before running script."
        )
        return

    if not (os.path.exists(parsed_args.input_dir) and
            os.path.isdir(parsed_args.input_dir)):
        LOGGER.error(
            "Given input dir, (%s) is either not a valid path or is not a directory",
            parsed_args.input_dir
        )
        return

    dir_iterator = Path(parsed_args.input_dir).iterdir()
    for file in dir_iterator:
        LOGGER.info("File: %s", file)
        print(json.dumps(ffmpeg.probe(file), indent=4))


if __name__ == "__main__":
    run()
