from io import StringIO

import pytest

from courier.article_index import PageRefCorrectionService
from courier.config import get_config

CORRFILE = get_config().metadata_dir / 'article_index_page_corrections.csv'


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
def test_split_page_ref_to_pages_returns_expected_values(page_ref, expected):
    result = PageRefCorrectionService(CORRFILE).split_page_ref_to_pages(page_ref)
    assert result == expected


# TODO: Expand tests, Use mocked CSV
def test_correct_returns_expected_values():

    c = StringIO(
        """courier_id;record_id;op;page
68988;68978;DELETE;8
74686;52516;DELETE;18
74686;52516;ADD;19
74686;52554;ADD;28
64933;64927;ADD;28-29
44515;187812;ADD;18-31"""
    )

    service = PageRefCorrectionService(c)
    result = service.correct(52516, [17, 18])
    assert result == [17, 19]
