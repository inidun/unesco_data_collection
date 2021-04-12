from pathlib import Path
from tempfile import TemporaryDirectory

from courier.config import get_config
from courier.tesseract_extract import extract_text

CONFIG = get_config()


# Test if python-pdfbox works


def test_extract_text_tesseract_extracts_right_amount_of_files():
    with TemporaryDirectory() as output_dir:
        extract_text(CONFIG.test_files_dir, output_folder=output_dir, dpi=1, fmt='png')

        assert len(list(Path(output_dir).iterdir())) == 8
