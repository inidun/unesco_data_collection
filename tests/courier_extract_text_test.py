import filecmp
from pathlib import Path
from tempfile import TemporaryDirectory

import pdfbox
import pytest

from courier.config import CourierConfig

CONFIG = CourierConfig()


# Test if python-pdfbox works
def test_python_pdfbox_extract_text_generates_correct_output():

    file = CONFIG.test_files_dir / "112488eng.pdf"
    expected_output = CONFIG.test_files_dir / "112488eng.txt"
    p = pdfbox.PDFBox()

    with TemporaryDirectory() as output_dir:
        output_path = (Path(output_dir) / f'{file.stem}.txt').resolve()
        p.extract_text(file, output_path=output_path)

        assert output_path.exists()
        assert len(list(Path(output_dir).iterdir())) == 1
        assert filecmp.cmp(output_path, expected_output) is True


@pytest.mark.skip(reason="TODO")
def extract_text_generates_expected_output():
    pass
    # extract_text(CONFIG.test_files_dir, CONFIG.test_files_dir / "boxout")
