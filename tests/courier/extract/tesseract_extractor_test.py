from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pytesseract

from courier.config import get_config
from courier.extract.interface import ITextExtractor
from courier.extract.tesseract_extractor import TesseractExtractor
from courier.extract.utils import get_filenames

CONFIG = get_config()


def test_tesseract_language_support():
    assert 'eng' in pytesseract.get_languages()
    assert set(pytesseract.get_languages()) >= {'eng', 'osd'}


def test_tesseract_version():
    assert pytesseract.get_tesseract_version().release >= (5, 5, 0)
    assert pytesseract.get_tesseract_version().public == '5.5.0'


def test_extract_extracts_right_amount_of_files():
    with TemporaryDirectory() as output_dir:
        files: List[Path] = get_filenames(CONFIG.test_files_dir / 'test.pdf')
        extractor: ITextExtractor = TesseractExtractor(dpi=1, fmt='png')
        extractor.batch_extract(files, output_dir)

        assert len(sorted(Path(output_dir).glob('*.txt'))) == 8
        assert (Path(output_dir) / 'extract.log').exists()
