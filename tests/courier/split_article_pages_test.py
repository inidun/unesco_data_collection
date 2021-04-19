import pytest

from courier.config import get_config
from courier.overlap_check import get_overlapping_pages
from courier.split_article_pages import create_regexp, get_stats

CONFIG = get_config()


def test_create_regexp():
    title = 'A nice and happy! title.? 77Maybe#'
    expr = create_regexp(title)
    assert isinstance(expr, str)
    assert expr == '[^a-zåäö]+nice[^a-zåäö]+and[^a-zåäö]+happy[^a-zåäö]+title[^a-zåäö]+maybe'


def test_get_stats():
    stats = get_stats(
        article_index=CONFIG.article_index,
        overlap=get_overlapping_pages(CONFIG.article_index)[:3],
    )
    assert stats.shape == (3, 6)


@pytest.mark.skip(reason='TODO')
def test_save_stats():  # Use tmp_path
    pass
    # stats = get_stats(
    #     article_index=CONFIG.article_index,
    #     overlap=get_overlapping_pages(CONFIG.article_index)[:3],
    # )
    # stats.to_csv(CONFIG.base_data_dir / 'overlap_match_stats.csv', index=False, sep='\t')
