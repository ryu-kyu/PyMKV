import os
import sys
import platform
import subprocess
import argparse
import json
import logger
import constants


LOGGER = logger.MKVLogger(__file__).logger


class MKVEditor:
    """
    Edit MKV files.
    """

    file_path: str

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        if platform.system() == constants.WINDOWS_OS:
            self.mkv_merge_exec = constants.MKV_MERGE_WIN
            self.mkv_prop_edit_exec = constants.MKV_PROP_EDIT_WIN
        else:
            LOGGER.error(
                "MKV Editor not yet implemented for %s or %s",
                constants.DARWIN_OS,
                constants.LINUX_OS,
            )
            sys.exit(1)

    def get_json_properties(self) -> dict:
        """
        Get MKV file properties
        """
        cmd = [self.mkv_merge_exec, "-J", self.file_path]
        LOGGER.info(f"MKVEditor: get_json_properties with cmd: {cmd}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def set_force_default_track(self, track_uid: str, is_on: bool) -> None:
        """
        Set 'Default track' and 'Forced display' flags for given track UID
        to True.
        :param track_uid: UID of track
        :param is_on: whether to set flags on or off
        """
        default_flag = "flag-default=1"
        forced_flag = "flag-forced=1"
        if not is_on:
            default_flag = "flag-default=0"
            forced_flag = "flag-forced=0"
        cmd = [
            self.mkv_prop_edit_exec,
            self.file_path,
            "--edit",
            f"track:={track_uid}",
            "--set",
            default_flag,
            "--set",
            forced_flag,
        ]
        LOGGER.info(f"MKVEditor: set_force_default_track with cmd: {cmd}")
        subprocess.run(
            cmd,
            check=True,
        )

    def remove_title_header(self) -> None:
        """
        Remove 'Title' element under 'Header > Segment' properties.
        """
        cmd = [
            self.mkv_prop_edit_exec,
            self.file_path,
            "--edit",
            "info",
            "--delete",
            "title",
        ]
        LOGGER.info(f"MKVEditor: remove_title_header with cmd: {cmd}")
        subprocess.run(
            cmd,
            check=True,
        )


def list_tracks(file_path: str) -> tuple[list[str]]:
    """
    List subtitle and audio tracks of an MKV file.
    :param file_path: Path to MKV file
    :return: Subtitle Tracks and Audio Tracks of MKV File
    """
    try:
        mkv_instance = MKVEditor(file_path)
        track_data = mkv_instance.get_json_properties()
        subtitle_tracks = []
        audio_tracks = []

        for track in track_data.get("tracks", []):
            uid = track["properties"]["uid"]
            if track["type"] == "subtitles":
                track_name = track["properties"].get("track_name", "No name")
                language = track["properties"].get("language", "unknown")
                subtitle_tracks.append((uid, language, track_name))
            elif track["type"] == "audio":
                language = track["properties"].get("language", "unknown")
                audio_tracks.append((uid, language))

        return subtitle_tracks, audio_tracks
    except subprocess.CalledProcessError as e:
        LOGGER.error(f"Error reading MKV file: {file_path}\n{e}")
        return [], []


def modify_file(file_path: str, subtitle_id: str, audio_id: str) -> None:
    """
    Modify an MKV file based on user selection.
    :param file_path: Path to MKV file
    :param subtitle_id: ID of subtitle track
    :param audio_id: ID of audio track
    """
    mkv_instance = MKVEditor(file_path)
    # Set default and forced flags for the selected subtitle track
    mkv_instance.set_force_default_track(subtitle_id, True)

    # Set default and forced flags for the selected audio track
    mkv_instance.set_force_default_track(audio_id, True)

    # Clear flags for all other tracks
    subtitle_tracks, audio_tracks = list_tracks(file_path)
    for track_id, _, _ in subtitle_tracks:
        if track_id == subtitle_id:
            continue
        mkv_instance.set_force_default_track(track_id, False)
    for track_id, _ in audio_tracks:
        if track_id == audio_id:
            continue
        mkv_instance.set_force_default_track(track_id, False)

    # Remove the title from segment information
    mkv_instance.remove_title_header()


def modify_files_in_dir(directory: str) -> None:
    """
    Modifies MKV files in directory
    :param directory: File path to directory
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".mkv"):
                file_path = os.path.join(root, file)
                LOGGER.info(f"\nProcessing file: {file_path}")

                subtitle_tracks, audio_tracks = list_tracks(file_path)
                if not subtitle_tracks or not audio_tracks:
                    LOGGER.warn("No subtitle or audio tracks found. Skipping file.")
                    continue

                # Display and select subtitle track
                LOGGER.info("\nSubtitle Tracks:")
                for i, (track_id, lang, name) in enumerate(subtitle_tracks):
                    LOGGER.info(
                        f"{i + 1}. Track ID: {track_id}, Language: {lang}, Name: {name}"
                    )
                while True:
                    stdin = input("Select subtitle track (number): ")
                    if stdin != "":
                        if (
                            stdin.isdigit()
                            and int(stdin) <= len(subtitle_tracks)
                            and int(stdin) >= 0
                        ):
                            break
                    print("Invalid input. Please enter a valid number.")
                sub_choice = int(stdin) - 1
                subtitle_id = subtitle_tracks[sub_choice][0]

                # Display and select audio track
                LOGGER.info("\nAudio Tracks:")
                for i, (track_id, lang) in enumerate(audio_tracks):
                    LOGGER.info(f"{i + 1}. Track ID: {track_id}, Language: {lang}")
                while True:
                    stdin = input("Select audio track (number): ")
                    if stdin != "":
                        if (
                            stdin.isdigit()
                            and int(stdin) <= len(audio_tracks)
                            and int(stdin) >= 0
                        ):
                            break
                    print("Invalid input. Please enter a valid number.")
                aud_choice = int(stdin) - 1
                audio_id = audio_tracks[aud_choice][0]

                # Modify the file
                modify_file(file_path, subtitle_id, audio_id)
                LOGGER.info(f"Modification complete for {file_path}!")


def parse_args(raw_args: list[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Modify MKV files' tracks and metadata."
    )
    parser.add_argument(
        "--directory",
        help="Directory containing MKV files.",
        required=True,
    )
    parser.epilog = """Example:

    poetry run pymkv/mkveditor.py --directory C:\\Users\\kyuhy\\Downloads\\Videos
    """
    args = parser.parse_args(raw_args)
    return args


def run(raw_args: list[str] = None) -> None:
    args = parse_args(raw_args)

    LOGGER.info("On Windows, run script through PowerShell!")

    modify_files_in_dir(args.directory)


if __name__ == "__main__":
    run()
