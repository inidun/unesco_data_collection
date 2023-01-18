from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from courier.config import get_config
from courier.overlap_check import (
    get_articles_with_overlap_of_two_or_more_other_articles,
    get_overlapping_pages,
    save_overlapping_pages,
)

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


@pytest.fixture
def article_index():
    statistics = StringIO(
        """courier_id;year;record_number;pages;catalogue_title;authors
111111;2020;111;[1];a1;a
111111;2020;111;[1];a2;b
111111;2020;111;[1];a3;
222222;2020;222;[1];b1;d
222222;2020;222;[1];b2;
"""
    )
    return pd.read_csv(statistics, sep=';')


def test_get_articles_with_overlap_of_two_or_more_other_articles(article_index):  # pylint: disable=redefined-outer-name
    df = get_articles_with_overlap_of_two_or_more_other_articles(article_index)
    assert df.shape == (1, 3)
    assert df.iloc[0].record_number == 111
