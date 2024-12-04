import os
import argparse
import logger

from typing import List


LOGGER = logger.MKVLogger(__file__).logger


def parse_args(raw_args: List[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename all files in a directory with given filename",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--file",
        help="Path to text file containing list of new filenames",
        default=None,
        required=True,
    )
    parser.add_argument(
        "--dest-folder",
        help="Path to folder containing files to be renamed",
        default=None,
        required=True,
    )
    parser.add_argument(
        "--num-seasons",
        help="Number of seasons to iterate through in (--file), delimited by s<season #>",
        default=0,
        required=False,
        type=int,
    )
    parser.epilog = """Example:
    
    poetry run pymkv/renamer.py --file ./eps.txt --dest-folder C:\\Users\\kyuhy\\Downloads\\Videos
    """

    parsed_args = parser.parse_args(raw_args)
    return parsed_args


def rename_files(args: argparse.Namespace) -> None:
    with open(args.file, "r") as f:
        lines = f.readlines()

    eps = []
    seasons_delimiter = (
        [] if args.num_seasons == 0 else [f"s{i}" for i in range(1, args.num_seasons)]
    )
    for i in range(len(lines)):
        if len(seasons_delimiter) == 0:
            if lines[i] == "\n":
                continue
            line = lines[i].strip()
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

    filenames = os.listdir(args.dest_folder)

    if len(filenames) != len(eps):
        LOGGER.error("# of files in folder does not match number of new filenames")
        LOGGER.debug(
            f"Folder has ({len(filenames)}) videos but text file has ({len(eps)}) names"
        )
        return

    for idx, filename in enumerate(filenames):
        if not filename.endswith(".mkv"):
            continue
        prev_filename = os.path.join(args.dest_folder, filename)
        new_filename = f"0{idx + 1}. {eps[idx]}.mkv"
        if idx > 8:
            new_filename = f"{idx + 1}. {eps[idx]}.mkv"
        new_filename = os.path.join(args.dest_folder, new_filename)

        os.rename(prev_filename, new_filename)


def run(raw_args: List[str] = None) -> None:
    args = parse_args(raw_args)

    if not os.path.exists(args.file):
        LOGGER.error("Given file path (--file) not found")
        return
    if not os.path.exists(args.dest_folder):
        LOGGER.error("Given file path (--dest-folder) not found")
        return

    rename_files(args)


if __name__ == "__main__":
    run()
