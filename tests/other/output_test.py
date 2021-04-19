import pandas as pd
import pytest

from courier.config import get_config
from courier.utils import get_stats

CONFIG = get_config()


@pytest.mark.skip(reason='Slow')
def test_all_files_extracted():
    stats = get_stats()
    assert len(list(CONFIG.pdf_dir.iterdir())) == stats['files'] == 671
    assert len(list(CONFIG.pdfbox_xml_dir.iterdir())) == stats['files'] == 671
    assert len(list(CONFIG.pdfbox_txt_dir.iterdir())) == stats['pages'] == 27336


def test_all_articles_extracted():
    assert len(list((CONFIG.article_output_dir / 'xml').iterdir())) == len(CONFIG.article_index)
    assert len(list((CONFIG.article_output_dir / 'txt').iterdir())) == len(CONFIG.article_index)
    assert len(pd.read_csv(CONFIG.article_output_dir / 'article_index.csv', sep='\t')) == 7612
