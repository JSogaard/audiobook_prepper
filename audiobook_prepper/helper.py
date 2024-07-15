import sys
import subprocess
from pathlib import Path
from typing import NamedTuple
from tempfile import NamedTemporaryFile
import glob
from mutagen.easyid3 import EasyID3
from mutagen.id3._util import ID3NoHeaderError
from mutagen.mp3 import MP3
from rich.console import Console

console = Console()

class NoFileInput(Exception):
    pass


def parse_paths(paths: list[str]) -> list[str]:
    """
    Parses the provided paths and returns a sorted list of files matching the paths.

    If the paths contain wildcard characters (* or ?), it uses glob to match files.

    Args:
        paths (str): Paths to be parsed.

    Returns:
        list[str]: Sorted list of file paths.
    """
    if not paths:
        raise NoFileInput

    path_list: list[str] = list(paths)  # type: ignore[call-overload]
    # Initialize an empty list to store file paths
    files: list[str] = []
    # If there is only one path and it contains a wildcard, use glob to find files
    if len(path_list) == 1 and ("*" in path_list[0] or "?" in path_list[0]):
        files = glob.glob(path_list[0])
    else:
        path: str
        for path in path_list:
            # Use glob to find files for each path that contains a wildcard
            if "*" in path or "?" in path:
                files.extend(glob.glob(path))
            else:
                files.append(path)

    # Sort list, remove duplicates and return
    return sorted(list(set(files)))


def update_tag(file: str, tag: str, value: str) -> None:
    """
    Update the ID3 tag of a given audio file.

    Args:
        file (str): Path to the audio file.
        tag (str): ID3 tag to update.
        value (str): New value for the ID3 tag.
    """
    id3: EasyID3
    try:
        id3 = EasyID3(file)
    except ID3NoHeaderError:
        # Create a new EasyID3 object if no header is found
        id3 = EasyID3()
    except Exception as e:
        console.print(f"An error occured while processing the file: {file} - {e}", style="bold bright_red")
        return

    id3[tag] = value
    id3.save(file)


def batch_update_tag(files: list[str], tag: str, value: str) -> None:
    """
    Update the specified ID3 tag for a batch of files.

    Args:
        files (list[str]): List of paths to the audio files.
        tag (str): ID3 tag to update.
        value (str): New value for the ID3 tag.
    """
    file: str
    for file in files:
        update_tag(file, tag, value)


class Chapter(NamedTuple):
    """
    Represents a chapter in an audiobook with its duration,
    start time and end time.

    Attributes:
        name (str): The name of the chapter.
        duration (int): The duration of the chapter in milliseconds.
        start (int): The start time of the chapter in milliseconds.
        end (int): The end time of the chapter in milliseconds.
    """

    name: str
    duration: int
    start: int
    end: int


def generate_ffmetadata(files: list[str]) -> str:
    """
    Generate a list of Chapter objects for the given audio files.

    Args:
        files (list[str]): List of paths to the audio files.

    Returns:
        list[Chapter]: List of Chapter objects.
    """
    ffmetadata: str = (
        f""";FFMETADATA
title=Empty
artist=Empty
genre=AudioBook"""
    )
    playhead: int = 0

    for file in files:
        try:
            mp3 = MP3(file)
            id3 = EasyID3(file)
        except Exception as e:
            sys.exit(
                f"An error occured while processing the file: {file} - {e}\nCould not proceed."
            )

        name: str = id3["title"][0]
        duration: int = int(mp3.info.length * 1000)
        start: int = playhead
        end: int = playhead + duration

        ffmetadata += f"""
[CHAPTER]
TIMEBASE=1/1000
START={start}
END={end}
title={name}"""

        playhead = end

    return ffmetadata


def get_bitrate(file: str) -> int:
    """
    Retrieve the bitrate of the given audio file.

    Args:
        file (str): Path to the audio file.

    Returns:
        int: The bitrate of the audio file.
    """
    try:
        return int(MP3(file).info.bitrate / 1000)  # type: ignore
    except Exception as e:
        sys.exit(
            f"An error occured while processing the file: {file} - {e}\nCould not proceed."
        )


def concatenate_audio(files: list[str], output: str, bitrate: int) -> None:
    """
    Concatenate multiple audio files into a single output file with the specified bitrate.

    Args:
        files (list[str]): List of paths to the audio files to be concatenated.
        output (str): Path to save the concatenated output file.
        bitrate (int): The bitrate for the output file.
    """
    if not bitrate:
        bitrate = get_bitrate(files[0])

    file_tmp_lines: list[str] = [
        f"file '{str(Path(file).resolve())}'" for file in files
    ]

    with NamedTemporaryFile("w+t") as files_tmp, NamedTemporaryFile(
        "w+t"
    ) as metadata_tmp:
        files_tmp.write("\n".join(file_tmp_lines))
        files_tmp.flush()

        metadata_tmp.write(generate_ffmetadata(files))
        metadata_tmp.flush()

        command: list[str] = [
            "ffmpeg",
            "-v",
            "info",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            files_tmp.name,
            "-i",
            metadata_tmp.name,
            "-map_metadata",
            "1",
            "-c:a",
            "aac",
            "-b:a",
            f"{bitrate}k",
            output,
        ]
        subprocess.run(command, check=True)
