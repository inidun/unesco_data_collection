# pylint: disable=redefined-outer-name
from io import StringIO

import pandas as pd
import pytest

from courier.article_index import PageRefCorrectionService
from courier.config import get_config


@pytest.fixture
def corrfile():
    return StringIO(
        """courier_id;record_id;op;page
68988;68978;DELETE;8
74686;52516;DELETE;18
74686;52516;ADD;19
74686;52554;ADD;28
64933;64927;ADD;28-29
44515;187812;ADD;18-31"""
    )


@pytest.mark.parametrize(
    'page_ref, expected',
    [
        ('2, 4-6', [2, 4, 5, 6]),
        ('1-2, 4, 6-7', [1, 2, 4, 6, 7]),
        ('4, 1-2', [1, 2, 4]),
        ('4 , 1-   2', [1, 2, 4]),
        ('4, 6-2', [4]),
        ('1-4, 2', [1, 2, 3, 4]),
    ],
)
def test_split_page_ref_to_pages_returns_expected_values(page_ref, expected, corrfile):
    result = PageRefCorrectionService(corrfile).split_page_ref_to_pages(page_ref)
    assert result == expected


# TODO: Expand tests
def test_correct_returns_expected_values(corrfile):
    service = PageRefCorrectionService(corrfile)
    result = service.correct(52516, [17, 18])
    assert result == [17, 19]


def get_record_info(article_index: pd.DataFrame, record_number: int) -> dict:
    return article_index[article_index['record_number'] == record_number].iloc[0].to_dict()


@pytest.mark.parametrize(
    'record_number, expected',
    [
        (187812, [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]),
        (64927, [28, 29]),
        (68978, [9, 10, 11]),
        (52516, [19]),
        (52554, [25, 26, 27, 28]),
        (73971, [])
    ],
)
def test_get_article_index_from_file_contains_correct_pages(record_number, expected):
    pages = get_record_info(get_config().article_index, record_number)['pages']
    assert pages == expected
