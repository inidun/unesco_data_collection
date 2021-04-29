from pathlib import Path

import pandas as pd
import pytest

from courier.config import get_config
from courier.utils import pdf_stats

CONFIG = get_config()


@pytest.mark.skip(reason='Slow')
def test_all_files_extracted():
    stats = pdf_stats()
    assert len(list(CONFIG.pdf_dir.iterdir())) == stats['files'] == 671
    assert len(list(CONFIG.xml_dir.iterdir())) == stats['files'] == 671
    assert len(list(Path(CONFIG.pages_dir / 'pdfbox').iterdir())) == stats['pages'] == 27336
    # TODO: assert len(list(Path(CONFIG.pages_dir / 'tesseract').iterdir())) == stats['pages'] == 27336


def test_all_articles_extracted():
    assert len(list((CONFIG.articles_dir / 'xml').iterdir())) == len(CONFIG.article_index)
    assert len(list((CONFIG.articles_dir / 'txt').iterdir())) == len(CONFIG.article_index)
    assert len(pd.read_csv(CONFIG.articles_dir / 'article_index.csv', sep='\t')) == 7612
