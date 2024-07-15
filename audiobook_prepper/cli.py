import os
import typer
from mutagen.easyid3 import EasyID3
from tabulate import tabulate # type:ignore
from audiobook_prepper.helper import *

app = typer.Typer()


TAGS: list[str] = [
    "title",
    "album",
    "artist",
    "albumartist",
    "composer",
    "discnumber",
    "tracknumber",
]


@app.command()
def show_tags(paths: list[str]) -> None:
    """
    Display the ID3 tags of the specified audio files in a table format.

    Args:
        paths (list[str]): Paths to the files whose tags need to be displayed.
    """
    files: list[str] = parse_paths(paths)
    table: list[list[str]] = [
        [
            "File",
            "Title",
            "Album",
            "Author",
            "Album Artist",
            "Narrator",
            "Disc",
            "Track",
        ]
    ]
    file: str
    row: list[str]
    for file in files:
        row = [os.path.basename(file)]
        try:
            id3: EasyID3 = EasyID3(file)
        except Exception as e:
            click.echo(f"An error occured while processing the file: {file} - {e}")
            return

        for tag in TAGS:
            row.append(id3[tag][0])
        table.append(row)

    click.echo("Give the terminal windows some width to display table properly.")
    click.echo(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))


@app.command()
def number_files(paths: list[str], start: int = 1) -> None:
    """
    Update the track number tag of each file with a sequential number,
    starting from the specified value.

    Args:
        paths (click.Path): Paths to the files to be updated.
        start (int): The starting number for the track numbering.
    """

    files: list[str] = parse_paths(paths)

    number: int
    file: str
    for number, file in enumerate(files, start=start):
        update_tag(file, "tracknumber", str(number))


@app.command()
def chapter_number(naming_scheme: str, paths: list[str], start: int = 1) -> None:
    """
    Update the title tag of each file with a name based on a naming scheme,
    replacing '%n' with a sequential number, starting from specified value.

    Args:
        naming_scheme (str): The naming scheme for the title, where '%n' will be replaced by the number.
        paths (click.Path): Paths to the files to be updated.
        start (int): The starting number for the chapter numbering.
    """

    files: list[str] = parse_paths(paths)

    number: int
    file: str
    for number, file in enumerate(files, start=start):
        new_title = naming_scheme.replace("%n", str(number))
        update_tag(file, "title", new_title)


@app.command()
def change_title(title_name: str, paths: list[str]) -> None:
    """
    Change the title tag of each specified file to the given title.

    Args:
        title_name (str): The new title to set for the files.
        paths (list[str]): Paths to the files to be updated.
    """
    batch_update_tag(parse_paths(paths), "title", title_name)


@app.command()
def change_author(author_name: str, paths: list[str]) -> None:
    """
    Change the author tag of each specified file to the given author name.

    Args:
        author_name (str): The new author name to set for the files.
        paths (list[str]): Paths to the files to be updated.
    """
    batch_update_tag(parse_paths(paths), "author", author_name)


@app.command()
def change_narrator(narrator_name: str, paths: list[str]) -> None:
    """
    Change the narrator (composer) tag of each specified file to the given narrator name.

    Args:
        narrator_name (str): The new narrator name to set for the files.
        paths (list[str]): Paths to the files to be updated.
    """
    batch_update_tag(parse_paths(paths), "composer", narrator_name)


@app.command()
def change_tag(tag: str, value: str, paths: list[str]) -> None:
    """
    Change a specified tag of each file to the given value.

    Args:
        tag (str): The tag to be changed.
        value (str): The new value for the tag.
        paths (list[str]): Paths to the files to be updated.
    """
    batch_update_tag(parse_paths(paths), tag, value)


@app.command()
def combine_files(
    paths: list[str], output: str = "output.m4b", bitrate: int = 64
) -> None:
    """
    Combine multiple audio files into a single file, with chapter markers.

    Args:
        paths (list[str]): Paths to the files to be combined.
        use_chapters (bool): Whether to use chapter markers in the output file.
        output (str): The path to save the combined output file.
        bitrate (int): The bitrate to use for the output file.
    """
    files: list[str] = parse_paths(paths)

    ffmetadata: str = generate_ffmetadata(files)

    concatenate_audio(files, output=output, bitrate=bitrate)


if __name__ == "__main__":
    app()
