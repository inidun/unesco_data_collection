import pandas as pd

from courier.config import get_config
from courier.overlap_check import get_overlapping_pages
from courier.split_article_pages import create_regexp, get_stats, save_stats

CONFIG = get_config()


def test_create_regexp():
    title = 'A nice and happy! title.? 77Maybe#'
    expr = create_regexp(title)
    assert isinstance(expr, str)
    assert expr == '[^a-zåäö]+nice[^a-zåäö]+and[^a-zåäö]+happy[^a-zåäö]+title[^a-zåäö]+maybe'


def test_get_stats_collects_both_found_and_not_found():
    stats = get_stats(
        article_index=CONFIG.article_index,
        overlap=get_overlapping_pages(CONFIG.article_index)[:3],
    )
    assert stats.shape == (3, 6)


def test_get_stats_returns_expected_values():
    stats = get_stats(
        article_index=CONFIG.article_index.loc[14255],
        overlap=get_overlapping_pages(CONFIG.article_index.loc[14255]),
    )
    assert stats.shape == (1, 6)
    assert stats.values.tolist()[0] == ['014255', 36, 36, 2, 0, 2]


def test_get_stats_logs_mismatches(caplog):
    get_stats(
        article_index=CONFIG.article_index.loc[14255],
        overlap=pd.DataFrame({'courier_id': {0: 14255}, 'page': {0: 36}, 'count': {0: 1}}),
    )
    assert 'Page count mismatch' in caplog.text


def test_save_stats(monkeypatch, tmp_path):
    monkeypatch.setattr(CONFIG, 'article_index', CONFIG.article_index.loc[14255])
    save_stats(tmp_path / 'overlap_stats.csv')
    assert (tmp_path / 'overlap_stats.csv').exists()
