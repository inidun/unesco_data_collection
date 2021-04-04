import filecmp
from pathlib import Path
from tempfile import TemporaryDirectory

import pdfbox
import pytest

from courier.config import CourierConfig
from courier.extract_text_pdfbox import extract_text as extract_text_pdfbox
from courier.extract_text_tesseract import extract_text as extract_text_tesseract

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


@pytest.mark.skip(reason="Too slow, test with fewer files")
def test_extract_text_pdfbox_generates_expected_output():
    with TemporaryDirectory() as output_dir:
        extract_text_pdfbox(CONFIG.test_files_dir, output_dir)

        assert len(list(Path(output_dir).iterdir())) == 212
        assert filecmp.dircmp(output_dir, CONFIG.test_files_dir / "pdfbox_out").diff_files == []


def test_extract_text_tesseract_extracts_right_amount_of_files():
    with TemporaryDirectory() as output_dir:
        extract_text_tesseract(CONFIG.test_files_dir, output_folder=output_dir, dpi=1, fmt="png")

        assert len(list(Path(output_dir).iterdir())) == 212
