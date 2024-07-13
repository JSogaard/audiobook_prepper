from click.testing import CliRunner
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
import audiobook_prepper

files: list[str] = [
    "./test_audiobook/01.mp3",
    "./test_audiobook/02.mp3",
    "./test_audiobook/03.mp3",
    "./test_audiobook/04.mp3",
    "./test_audiobook/05.mp3",
]

def test_number_files_arglist():
    runner = CliRunner()
    result = runner.invoke(
        audiobook_prepper.number_files,
        [
            "number",
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
    for number, file in enumerate(files, start=2):
        id3 = EasyID3(file)
        assert id3["tracknumber"] == str(number)
