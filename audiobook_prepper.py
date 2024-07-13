from pprint import pprint
import click
import glob
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError


def parse_paths(paths: click.Path) -> list[str]:
    """
    Parses the provided paths and returns a sorted list of files matching the paths.

    If the paths contain wildcard characters (* or ?), it uses glob to match files.

    Args:
        paths (click.Path): Paths to be parsed.

    Returns:
        list[str]: Sorted list of file paths.
    """
    path_list: list[str] = list(paths)  # type: ignore[call-overload]
    # Initialize an empty list to store file paths
    files: list = []
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
        click.echo(f"An error occured while processing the file: {file} - {e}")
        return

    id3[tag] = value
    id3.save(file)


@click.group()
def cli() -> None:
    """Tool to prepare audiobook files."""
    pass
    # TODO Read up on Click groups

@cli.command(name="showtags")
@click.argument("path", type=click.Path(exists=True), nargs=1)
def show_tags(path: str):
    try:
        id3 = EasyID3(path)
        click.echo(pprint(dict(id3)))
    except Exception as e:
                click.echo(f"An error occured while processing the file: {path} - {e}")

@cli.command(name="number")
@click.argument("paths", type=click.Path(), nargs=-1)
@click.option("--start", type=int, default=1, show_default=True)
def number_files(paths: click.Path, start: int) -> None:
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


@cli.command(name="chapternumber")
@click.argument("naming_scheme", type=str, nargs=1)
@click.argument("paths", type=click.Path(), nargs=-1)
@click.option("--start", type=int, default=1, show_default=True)
def chapter_number(naming_scheme: str, paths: click.Path, start: int) -> None:
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


@cli.command(name="changeauthor")
@click.argument("author_name", type=str, nargs=1)
@click.argument("paths", type=click.Path(), nargs=-1)
def change_author(author_name: str, paths: click.Path):
    
    files: list[str] = parse_paths(paths)
    
    file: str
    for file in files:
        update_tag(file, "author", author_name)

    # TODO Tests


def change_narrator():
    ...
    # TODO Narrator/composer function


def combine_files():
    ...
    # TODO Combine files function


if __name__ == "__main__":
    cli()
