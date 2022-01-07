from typing import Union

import pandas as pd
import pytest

from courier.article_index import (
    article_index_to_csv,
    get_article_index_from_file,
    get_courier_id,
    get_english_host_item,
    get_expanded_article_pages,
    get_issue_index_from_file,
)
from courier.config import get_config

CONFIG = get_config()


@pytest.mark.parametrize(
    'test_input_host_item, expected',
    [
        ('English title first eng|Other Title|eng keyword in wrong place', 'English title first eng'),
        ('Non-english title|English title not first eng|Another non-english title', 'English title not first eng'),
        ('No english title', None),
    ],
)
def test_get_english_host_item_returns_expected_values(test_input_host_item, expected):
    result = get_english_host_item(test_input_host_item)
    assert result == expected


def test_get_english_host_with_multiple_valid_host_items_raises_value_error():
    with pytest.raises(ValueError, match="duplicate.*'First eng', 'Second eng'"):
        get_english_host_item('First eng|Second eng')


@pytest.mark.parametrize(
    'test_input_eng_host_item, expected',
    [
        ('Fill zeroes 123 eng', '000123'),
        ('Text before 77050 eng', '077050'),
    ],
)
def test_get_courier_id_returns_expected_values(test_input_eng_host_item, expected):
    result = get_courier_id(test_input_eng_host_item)
    assert result == expected
    assert len(result) == 6


def test_get_courier_id_with_missing_id_returns_none():
    assert get_courier_id('No matching ID eng') is None


def test_get_courier_id_with_no_title_returns_none():
    assert get_courier_id('123456 eng') is None


def test_get_courier_id_with_invalid_id_raises_value_error():
    with pytest.raises(ValueError):  # , match='must be <= 6'):
        get_courier_id('Title 1234567 eng')


@pytest.mark.parametrize(
    'test_input_page_refs, expected',
    [
        (None, []),
        ('p. 1-2', [1, 2]),
        ('p. 1', [1]),
        ('p. 1, 2 ', [1, 2]),
        ('p. 1, 2-4 ', [1, 2, 3, 4]),
        ('p.1-2', [1, 2]),
        ('p.1-2,6', [1, 2, 6]),
        ('p.1', [1]),
        ('p.1, 3-4, 77', [1, 3, 4, 77]),
        ('p. 1-2, 4 ', [1, 2, 4]),
        ('page 1', [1]),
        ('page 1, 3, 5-6', [1, 3, 5, 6]),
        ('p., 1-2', [1, 2]),
        ('p. 1-2, 4-5 ', [1, 2, 4, 5]),
        ('p. 1, 2-3, 14-15, 77 ', [1, 2, 3, 14, 15, 77]),
        ('p. 15-16, 20-21, 31-32', [15, 16, 20, 21, 31, 32]),
        ('p. 4-8, 32', [4, 5, 6, 7, 8, 32]),
    ],
)
def test_get_expanded_article_pages_returns_exptected_values(test_input_page_refs, expected):
    result = get_expanded_article_pages(test_input_page_refs)
    assert result == expected


def test_get_article_index_from_file_returns_dataframe_with_expected_shape_and_content():
    article_index = get_article_index_from_file(CONFIG.metadata_file)
    assert len(article_index) == 7612
    assert article_index.shape == (7612, 5)
    assert not article_index.isnull().values.any()

    expected_columns = [
        'courier_id',
        'year',
        'record_number',
        'pages',
        'catalogue_title',
    ]

    assert set(article_index.columns) == set(expected_columns)
    assert article_index.columns.to_list() == expected_columns
    assert article_index.dtypes.to_list() == ['O', 'uint16', 'uint32', 'O', 'O']


@pytest.mark.parametrize(
    'record_number, expected',
    [
        (30745, [21, 27, 28, 29, 30]),
        (44634, [6, 7, 8, 9, 10, 11, 70]),
        (45102, [4, 5, 6, 7, 8, 32]),
        (45847, [16, 17, 18, 23, 26, 27]),
        (46398, [6, 9, 10]),
        (49572, [28, 29, 30, 46]),
        (50644, [24, 25, 26, 27, 32]),
        (58762, [15, 16, 20, 21, 31, 32]),
        (61141, [21, 28]),
        (62094, [17, 20, 21, 22]),
        (64927, [28, 29]),
        (65232, [4, 5, 6, 10, 11]),
        (68805, [13, 14, 16, 17]),
        (69987, [8, 9, 12, 13]),
        (70036, [11, 14, 15, 16, 17, 18, 19]),
        (73870, [1, 7]),
        (73872, [3, 7]),
        (73873, [3, 7]),
        (73877, [4, 5]),
        (86451, [22, 24, 25, 26]),
        (93658, [4, 5, 6, 7, 46, 47, 48]),
        (179481, [3, 4, 11]),
        (262393, [1, 12]),
    ],
)
def test_get_article_index_from_file_contains_correct_pages(record_number, expected):
    pages = get_record_info(record_number)['pages']
    assert pages == expected


def get_record_info(record_number: int) -> dict:
    article_index = get_article_index_from_file(CONFIG.metadata_file, CONFIG.correction_file)
    return article_index[article_index['record_number'] == record_number].iloc[0].to_dict()


def test_article_index_to_csv(tmp_path):
    article_index_to_csv(get_article_index_from_file(CONFIG.metadata_file, CONFIG.correction_file), tmp_path)
    assert (tmp_path / 'article_index.csv').exists()


def test_get_issue_index_from_file_has_no_empty_values():
    issue_index = get_issue_index_from_file(CONFIG.metadata_file)
    assert not issue_index.isnull().values.any()


def diff_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> Union[pd.DataFrame, pd.Series]:
    return pd.concat([df1, df2]).drop_duplicates(keep=False)


def test_article_index_has_not_changed():
    article_index = CONFIG.article_index.copy(deep=True)
    original_article_index = get_article_index_from_file(
        'tests/fixtures/courier/metadata/UNESCO_Courier_metadata.csv', CONFIG.correction_file
    )
    article_index.pages = article_index.pages.astype('str')
    original_article_index.pages = original_article_index.pages.astype('str')
    diff = diff_dataframes(article_index, original_article_index)
    assert diff.empty, 'Article index has been changed'


@pytest.mark.skip('pandas.util.testing is deprecated')
def test_diff_dataframes():
    df = pd._testing.makeDataFrame()  # pylint: disable=protected-access
    df_t = df.transpose()

    assert diff_dataframes(df, df).empty
    assert diff_dataframes(df_t, df_t).empty
    assert not diff_dataframes(df, df_t).empty
