from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from courier.config import get_config
from courier.extract.cli import extract, get_extractor
from courier.extract.pdfbox_extractor import PDFBoxExtractor
from courier.extract.pdfminer_extractor import PDFMinerExtractor
from courier.extract.pdfplumber_extractor import PDFPlumberExtractor
from courier.extract.tesseract_extractor import TesseractExtractor

CONFIG = get_config()


@pytest.mark.parametrize(
    'method, instance',
    [
        ('PDFBox', PDFBoxExtractor),
        ('PDFMiner', PDFMinerExtractor),
        ('PDFPlumber', PDFPlumberExtractor),
        ('Tesseract', TesseractExtractor),
    ],
)
def test_get_extractor_returns_subclass_of_itextextractor(method, instance):
    extractor = get_extractor(method)
    assert isinstance(extractor, instance)


def test_get_extractor_with_unknown_method_raises_value_error():
    with pytest.raises(ValueError):
        get_extractor('Unknown method')


@pytest.mark.parametrize(
    'extractor, first_page, last_page, expected',
    [
        ('PDFBox', 1, None, 5),
        ('PDFBox', 2, 100, 3),
        ('PDFBox', 100, None, 0),
        ('PDFMiner', 1, None, 5),
        ('PDFMiner', 2, 100, 3),
        ('PDFMiner', 100, None, 0),
        ('PDFPlumber', 1, None, 5),
        ('PDFPlumber', 2, 100, 3),
        ('PDFPlumber', 100, None, 0),
        ('Tesseract', 1, None, 5),  # FIXME: Patch tesseract settings
        ('Tesseract', 2, 100, 3),
        ('Tesseract', 100, None, 0),
    ],
)
def test_extract_text(extractor, first_page, last_page, expected):
    with TemporaryDirectory() as output_dir:
        extract(
            Path(CONFIG.test_files_dir / 'pdf'),
            output_dir,
            first_page=first_page,
            last_page=last_page,
            extractor=extractor,
        )
        result = len(sorted(Path(output_dir).glob('*.txt')))
        assert result == expected
        assert (Path(output_dir) / 'extract.log').exists()
