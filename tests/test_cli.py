from typer.testing import CliRunner
from mutagen.easyid3 import EasyID3
from audiobook_prepper import *

FILES: list[str] = [
    "./test_audiobook/01.mp3",
    "./test_audiobook/02.mp3",
    "./test_audiobook/03.mp3",
    "./test_audiobook/04.mp3",
    "./test_audiobook/05.mp3",
]


def test_number_files() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "number-files",
            "test_audiobook/*.mp3",
            "--start",
            "2",
        ],
    )
    assert result.exit_code == 0

    file: str
    number: int
    for number, file in enumerate(FILES, start=2):
        assert EasyID3(file)["tracknumber"] == [str(number)]


def test_chapter_number() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["chapter-number", "Chapter %n", "test_audiobook/*.mp3", "--start", "1"],
    )
    assert result.exit_code == 0

    file: str
    number: int
    for number, file in enumerate(FILES, start=1):
        assert EasyID3(file)["title"] == [f"Chapter {number}"]


def test_change_title() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["change-title", "Titly Title", "test_audiobook/*.mp3"])
    assert result.exit_code == 0

    file: str
    for file in FILES:
        assert EasyID3(file)["title"] == ["Titly Title"]


def test_change_author() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app, ["change-author", "Author McAuthorface", "test_audiobook/*.mp3"]
    )
    assert result.exit_code == 0

    file: str
    for file in FILES:
        assert EasyID3(file)["author"] == ["Author McAuthorface"]


def test_change_narrator() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app, ["change-narrator", "Narrator McNarrator", "test_audiobook/*.mp3"]
    )
    assert result.exit_code == 0

    file: str
    for file in FILES:
        assert EasyID3(file)["composer"] == ["Narrator McNarrator"]


def test_change_tag() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["change-tag", "composer", "Mozart", "test_audiobook/*.mp3"])
    assert result.exit_code == 0

    file: str
    for file in FILES:
        assert EasyID3(file)["composer"] == ["Mozart"]
