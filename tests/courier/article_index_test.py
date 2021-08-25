import pytest

from courier.article_index import (
    article_index_to_csv,
    get_article_index_from_file,
    get_courier_id,
    get_english_host_item,
    get_expanded_article_pages,
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
        ('p.1', [1]),
        ('p. 1-2, 4 ', [1, 2, 4]),
        ('page 1', [1]),
        ('p., 1-2', [1, 2]),
        ('p. 1-2, 4-5 ', [1, 2, 4, 5]),
        ('p. 1-2, 4-5 ', [1, 2, 4, 5]),
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

    expected_columns = [
        'record_number',
        'catalogue_title',
        'courier_id',
        'year',
        'pages',
    ]

    assert set(article_index.columns) == set(expected_columns)


# TODO Add failed + slumped
@pytest.mark.parametrize(
    'record_number, expected',
    [
        (58762, [15, 16, 20, 21, 31, 32]),
        (64927, [28, 29]),
    ],
)
def test_get_article_index_from_file_contains_correct_pages(record_number, expected):
    pages = get_record_info(record_number)['pages']
    assert pages == expected


def get_record_info(record_number: int) -> dict:
    article_index = get_article_index_from_file(CONFIG.metadata_file)
    return article_index[article_index['record_number'] == record_number].iloc[0].to_dict()


def test_article_index_to_csv(tmp_path):
    article_index_to_csv(get_article_index_from_file(CONFIG.metadata_file), tmp_path)
    assert (tmp_path / 'article_index.csv').exists()
