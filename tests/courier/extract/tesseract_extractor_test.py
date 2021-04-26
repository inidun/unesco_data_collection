from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from courier.config import get_config
from courier.extract.interface import ITextExtractor
from courier.extract.tesseract_extractor import TesseractExtractor
from courier.extract.utils import get_filenames

CONFIG = get_config()


def test_extract_extracts_right_amount_of_files():
    with TemporaryDirectory() as output_dir:

        files: List[Path] = get_filenames(CONFIG.test_files_dir / 'test.pdf')
        extractor: ITextExtractor = TesseractExtractor(dpi=1, fmt='png')
        extractor.extract(files, output_dir)

        assert len(list(Path(output_dir).iterdir())) == 8
