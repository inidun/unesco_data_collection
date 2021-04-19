from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from courier.config import get_config
from courier.overlap_check import get_overlapping_pages, save_overlapping_pages

CONFIG = get_config()


# FIXME: do proper testing
def test_get_overlapping_pages():
    overlapping_pages = get_overlapping_pages(CONFIG.article_index)
    op2 = pd.read_csv(CONFIG.overlapping_pages, sep='\t')
    assert overlapping_pages.equals(op2)


def test_save_overlapping_pages():
    with TemporaryDirectory() as output_dir:
        op = get_overlapping_pages(CONFIG.article_index)
        save_overlapping_pages(op, (Path(output_dir) / 'op.csv'))
        assert len(list(Path(output_dir).iterdir())) == 1
