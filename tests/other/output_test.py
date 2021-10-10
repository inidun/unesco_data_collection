import pytest

from courier.config import get_config
from courier.extract.utils import get_filenames
from courier.utils import pdf_stats

CONFIG = get_config()


@pytest.mark.slow
@pytest.mark.parametrize(
    'method, path',
    [
        ('XML', CONFIG.xml_dir),
        ('PDFBox', CONFIG.xml_dir / 'pdfbox'),
        ('PDFMiner', CONFIG.xml_dir / 'pdfminer'),
        ('PDFPlumber', CONFIG.xml_dir / 'pdfplumber'),
        pytest.param('Tesseract', CONFIG.xml_dir / 'tesseract', marks=pytest.mark.skip('Not all files extracted')),
    ],
)
def test_all_issues_extracted(method, path):
    expected = pdf_stats()['files']
    extracted = len(get_filenames(path, 'xml'))
    assert 671 == extracted == expected, method


@pytest.mark.slow
@pytest.mark.parametrize(
    'method, path',
    [
        ('PDFBox', CONFIG.pages_dir / 'pdfbox'),
        ('PDFMiner', CONFIG.pages_dir / 'pdfminer'),
        ('PDFPlumber', CONFIG.pages_dir / 'pdfplumber'),
        pytest.param('Tesseract', CONFIG.pages_dir / 'tesseract', marks=pytest.mark.skip('Not all files extracted')),
    ],
)
def test_all_pages_extracted(method, path):
    expected = pdf_stats()['pages']
    extracted = len(get_filenames(path, 'txt'))
    assert 27336 == extracted == expected, method


@pytest.mark.slow
@pytest.mark.parametrize(
    'method, path, extension',
    [
        ('XML (extract_articles.py)', CONFIG.articles_dir / 'xml', 'xml'),
        ('TXT (extract_articles.py)', CONFIG.articles_dir / 'txt', 'txt'),
        ('Export (elements.py)', CONFIG.articles_dir / 'exported', 'txt'),
    ],
)
def test_all_articles_extracted(method, path, extension):
    expected = len(CONFIG.article_index)
    extracted = len(get_filenames(path, extension))
    assert 7612 == extracted == expected, method
