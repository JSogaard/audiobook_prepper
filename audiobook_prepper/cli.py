import os
from tempfile import NamedTemporaryFile
import click
from mutagen.easyid3 import EasyID3
from tabulate import tabulate # type:ignore
from audiobook_prepper.helper import *


@click.group()
def cli() -> None:
    """Tool to prepare audiobook files."""
    pass
    # TODO Read up on Click groups


TAGS: list[str] = [
    "title",
    "album",
    "artist",
    "albumartist",
    "composer",
    "discnumber",
    "tracknumber",
]


@cli.command(name="show-tags")
@click.argument("paths", type=click.Path(), nargs=-1)
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


@cli.command(name="number")
@click.argument("paths", type=click.Path(), nargs=-1)
@click.option("-s", "--start", type=int, default=1, show_default=True)
def number_files(paths: list[str], start: int) -> None:
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


@cli.command(name="chapter-number")
@click.argument("naming-scheme", type=str, nargs=1)
@click.argument("paths", type=click.Path(), nargs=-1)
@click.option("-s", "--start", type=int, default=1, show_default=True)
def chapter_number(naming_scheme: str, paths: list[str], start: int) -> None:
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


@cli.command(name="change-title")
@click.argument("title-name", type=str, nargs=1)
@click.argument("paths", type=click.Path(), nargs=-1)
def change_title(title_name: str, paths: list[str]) -> None:
    """
    Change the title tag of each specified file to the given title.

    Args:
        title_name (str): The new title to set for the files.
        paths (list[str]): Paths to the files to be updated.
    """
    batch_update_tag(parse_paths(paths), "title", title_name)


@cli.command(name="change-author")
@click.argument("author-name", type=str, nargs=1)
@click.argument("paths", type=click.Path(), nargs=-1)
def change_author(author_name: str, paths: list[str]) -> None:
    """
    Change the author tag of each specified file to the given author name.

    Args:
        author_name (str): The new author name to set for the files.
        paths (list[str]): Paths to the files to be updated.
    """
    batch_update_tag(parse_paths(paths), "author", author_name)


@cli.command(name="change-narrator")
@click.argument("narrator-name", type=str, nargs=1)
@click.argument("paths", type=click.Path(), nargs=-1)
def change_narrator(narrator_name: str, paths: list[str]) -> None:
    """
    Change the narrator (composer) tag of each specified file to the given narrator name.

    Args:
        narrator_name (str): The new narrator name to set for the files.
        paths (list[str]): Paths to the files to be updated.
    """
    batch_update_tag(parse_paths(paths), "composer", narrator_name)


@cli.command(name="change-tag")
@click.argument("tag", type=str, nargs=1)
@click.argument("value", type=str, nargs=1)
@click.argument("paths", type=click.Path(), nargs=-1)
def change_tag(tag: str, value: str, paths: list[str]) -> None:
    """
    Change a specified tag of each file to the given value.

    Args:
        tag (str): The tag to be changed.
        value (str): The new value for the tag.
        paths (list[str]): Paths to the files to be updated.
    """
    batch_update_tag(parse_paths(paths), tag, value)


@cli.command(name="combine-files")
@click.argument("paths", type=click.Path(), nargs=-1)
@click.option("-c", "--use-chapters", type=bool, default=True, show_default=True)
@click.option(
    "-o", "--output", type=click.Path(), default="output.m4b", show_default=True
)
@click.option("-b", "--bitrate", type=int, default=None)
def combine_files(
    paths: list[str], use_chapters: bool, output: str, bitrate: int
) -> None:
    """
    Combine multiple audio files into a single file, with optional chapter markers.

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
    cli()
