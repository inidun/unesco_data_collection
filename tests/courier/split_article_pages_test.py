# pylint: disable=redefined-outer-name
import pandas as pd
import pytest

from courier.config import get_config
from courier.overlap_check import get_overlapping_pages
from courier.split_article_pages import (
    corrected_page_number,
    create_regexp,
    get_stats,
    match_fuzzywuzzy,
    match_regex,
    save_stats,
)

# TODO: test countinue_count
# TODO: test find_title_by_fuzzymatch
# TODO: test find_title_by_regex


@pytest.fixture(name='article_index')
def article_index():
    return get_config().article_index.copy(deep=True)


@pytest.mark.parametrize(
    'courier_id, page_number, expected',
    [
        ('012656', 10, 10),
        ('012656', 20, 19),
        ('069916', 25, 22),
        ('033144', 65, 65),
    ],
)
def test_corrected_page_number_returns_expected(courier_id, page_number, expected):
    result = corrected_page_number(courier_id, page_number)
    assert result == expected


def test_find_title_by_fuzzymatch_with_out_of_bounds_min_score_raises_value_error():
    with pytest.raises(ValueError, match='min_score'):
        match_fuzzywuzzy('test', 'test', min_score=101)
    with pytest.raises(ValueError, match='min_score'):
        match_fuzzywuzzy('test', 'test', min_score=-1)


def test_create_regexp():
    title = 'A nice and happy! title.? 77Maybe#'
    expr = create_regexp(title)
    assert isinstance(expr, str)
    assert expr == '[^a-zåäö]+nice[^a-zåäö]+and[^a-zåäö]+happy[^a-zåäö]+title[^a-zåäö]+maybe'


def test_get_stats_returns_dataframe_or_correct_size(article_index):
    stats = get_stats(
        article_index=article_index,
        overlap=get_overlapping_pages(article_index)[:3],
    )

    expected_columns = [
        'courier_id',
        'page',
        'page_corr',
        'count',
        'found',
        'not_found',
        'continued_count',
        'uppercase_count',
    ]

    assert stats.shape == (3, 8)
    assert set(stats.columns) == set(expected_columns)


@pytest.mark.parametrize(
    'courier_id, method, expected',
    [
        ('014255', match_regex, ['014255', 36, 36, 2, 0, 2, 1, 2]),
        ('014255', match_fuzzywuzzy, ['014255', 36, 36, 2, 0, 2, 1, 2]),
        ('059301', match_regex, ['059301', 30, 30, 2, 1, 1, 1, 1]),
        ('059301', match_fuzzywuzzy, ['059301', 30, 30, 2, 0, 2, 1, 1]),
    ],
)
def test_get_stats_returns_expected_values(courier_id, method, expected, article_index):
    stats = get_stats(
        article_index=article_index[article_index['courier_id'] == courier_id],
        overlap=get_overlapping_pages(article_index[article_index['courier_id'] == courier_id]),
        match_function=method,
    )
    result = stats.values.tolist()[0]
    assert result == expected


def test_get_stats_logs_mismatches(caplog, article_index):
    get_stats(
        article_index=article_index[article_index['courier_id'] == '014255'],
        overlap=pd.DataFrame({'courier_id': {0: 14255}, 'page': {0: 36}, 'count': {0: 1}}),
    )
    assert 'Page count mismatch' in caplog.text


def test_save_stats(tmp_path, article_index):
    index = article_index[article_index['courier_id'].isin(['014255', '015480'])]

    save_stats(index, tmp_path, 'regex')
    assert (tmp_path / 'overlap_stats_regex.csv').exists()

    save_stats(index, tmp_path, 'fuzzywuzzy')
    assert (tmp_path / 'overlap_stats_fuzzywuzzy.csv').exists()
