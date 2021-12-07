from pathlib import Path
from statistics import median
from typing import Dict

import pdf2image
import pytest

from courier.config import get_config
from courier.extract.utils import get_filenames

CONFIG = get_config()


def pdf_stats() -> Dict[str, int]:
    tot_pages = []
    for file in Path(CONFIG.pdf_dir).glob('*.pdf'):
        tot_pages.append(pdf2image.pdfinfo_from_path(file)['Pages'])
    return {
        'files': len(tot_pages),
        'pages': sum(tot_pages),
        'mean': round(sum(tot_pages) / len(tot_pages)),
        'median': round(median(tot_pages)),
    }


def test_pdf_stats(monkeypatch):
    monkeypatch.setattr(CONFIG, 'pdf_dir', CONFIG.test_files_dir)
    stats = pdf_stats()
    assert stats['files'] == 1
    assert stats['mean'] == 8
    assert stats['median'] == 8
    assert stats['pages'] == 8


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
    ],
)
def test_all_articles_extracted(method, path, extension):
    expected = len(CONFIG.article_index)
    extracted = len(get_filenames(path, extension))
    assert 7612 == extracted == expected, method


@pytest.mark.slow
def test_all_articles_exported():
    path = max([x for x in CONFIG.articles_dir.iterdir() if x.is_dir() and x.stem.startswith('exported')])
    expected = len(CONFIG.article_index)
    extracted = len(get_filenames(path, 'txt'))
    assert 7612 == extracted == expected
