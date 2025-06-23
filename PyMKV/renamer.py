import os
import argparse
import sys
import pathlib

import logger
import constants

from typing import List, Optional


LOGGER = logger.MKVLogger(__file__).logger


def parse_args(raw_args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename all files in a directory with given filename",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Path to text file containing list of new filenames",
        default=None,
        required=True,
    )
    parser.add_argument(
        "-d",
        "--directory",
        help="Path to folder containing files to be renamed",
        default=None,
        required=True,
    )
    parser.add_argument(
        "-n",
        "--num-seasons",
        help="Number of seasons to iterate through in (--file), delimited by s<season #>",
        default=0,
        required=False,
        type=int,
    )
    parser.epilog = """Example:
    
    poetry run pymkv/renamer.py --file ./eps.txt --directory C:\\Users\\user\\Downloads\\Videos
    """

    parsed_args = parser.parse_args(raw_args)
    return parsed_args


def rename_files(args: argparse.Namespace) -> None:
    with open(args.file, "r") as f:
        lines = f.readlines()

    eps: list[str] = []
    seasons_delimiter = (
        [] if args.num_seasons == 0 else [f"s{i}" for i in range(1, args.num_seasons)]
    )
    for i in range(len(lines)):
        if len(seasons_delimiter) == 0:
            if lines[i] == "\n":
                continue
            line = lines[i].strip()
            for invalid_char in constants.INVALID_PATH_CHARS:
                if invalid_char not in line:
                    continue
                LOGGER.error(
                    "Line called (%s) is contains an invalid file path character",
                    line,
                )
                LOGGER.warning(
                    "No files have been renamed... Aborting renamer script!",
                )
                sys.exit(1)
            if line:
                eps.append(line)
        else:
            for s_delimiter in seasons_delimiter:
                if lines[i].startswith(s_delimiter):
                    for j in range(i + 1, len(lines)):
                        if lines[j] == "\n":
                            break
                        line = lines[j].strip()
                        if line:
                            eps.append(line)

    filenames = os.listdir(str(args.directory))

    if len(filenames) != len(eps):
        LOGGER.error(
            "# of files in folder does not match number of new filenames",
        )
        LOGGER.debug(
            f"Folder has ({len(filenames)}) videos but text file "
            f"has ({len(eps)}) names"
        )
        return

    for idx, filename in enumerate(filenames):
        prev_filename = os.path.join(args.directory, filename)
        file_ext = pathlib.Path(prev_filename).suffix
        new_filename = f"0{idx + 1}. {eps[idx]}{file_ext}"
        if idx > 8:
            new_filename = f"{idx + 1}. {eps[idx]}{file_ext}"
        new_filename = os.path.join(args.directory, new_filename)

        os.rename(prev_filename, new_filename)

    LOGGER.info(
        f"Renaming successful! -- See directory {args.directory} for changes!",
    )


def run(raw_args: Optional[List[str]] = None) -> None:
    args = parse_args(raw_args)

    if not os.path.exists(args.file):
        LOGGER.error("Given file path (--file) not found")
        return
    if not os.path.exists(args.directory):
        LOGGER.error("Given file path (--directory) not found")
        return

    rename_files(args)


if __name__ == "__main__":
    run()
