from click.testing import CliRunner
from mutagen.easyid3 import EasyID3
import audiobook_prepper

FILES: list[str] = [
    "./test_audiobook/01.mp3",
    "./test_audiobook/02.mp3",
    "./test_audiobook/03.mp3",
    "./test_audiobook/04.mp3",
    "./test_audiobook/05.mp3",
]



def test_number_files():
    runner = CliRunner()
    result = runner.invoke(
        audiobook_prepper.number_files,
        [
            "test_audiobook/01.mp3",
            "test_audiobook/02.mp3",
            "test_audiobook/03.mp3",
            "test_audiobook/05.mp3",
            "test_audiobook/04.mp3",
            "--start",
            "2",
        ],
    )
    assert result.exit_code == 0

    id3: EasyID3
    file: str
    number: int
    for number, file in enumerate(FILES, start=2):
        id3 = EasyID3(file)
        assert id3["tracknumber"] == [str(number)]
