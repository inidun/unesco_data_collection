from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from courier.config import get_config
from courier.overlap_check import get_overlapping_pages, save_overlapping_pages

CONFIG = get_config()


def test_get_overlapping_pages_return_expected():
    overlapping_pages = get_overlapping_pages(CONFIG.article_index)
    expected = pd.read_csv(CONFIG.overlap_file, sep='\t')
    assert overlapping_pages.equals(expected)
    assert overlapping_pages.shape == (1246, 3)
    assert set(overlapping_pages.columns) == set(['courier_id', 'page', 'count'])


def test_save_overlapping_pages():
    with TemporaryDirectory() as output_dir:
        overlapping_pages = get_overlapping_pages(CONFIG.article_index)
        save_overlapping_pages(overlapping_pages, (Path(output_dir) / 'overlap.csv'))
        assert (Path(output_dir) / 'overlap.csv').exists()
