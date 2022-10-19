from os.path import basename, splitext

import pandas as pd
import pytest

from courier.config import get_config
from courier.scripts.tagged_issue_to_articles import get_issue_articles

CONFIG = get_config()


def test_get_issue_articles_returns_expected():

    filename = 'tests/fixtures/courier/tagged_issue/tagged_1234_123456.md'

    articles = get_issue_articles(filename)

    assert len(articles) == 2
    assert '78910' in articles.keys()
    assert len([x for x in articles.keys() if x.startswith('@')]) == 1
    assert articles['78910'][2].startswith('article text')
    assert '@123456-1' in articles.keys()


@pytest.mark.parametrize(
    'file',
    [
        ('tagged_1952_070990.md'),
        ('tagged_1972_052257.md'),
    ],
)
def test_get_issue_articles_returns_values_agreeing_with_index(file):

    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename)

    _, _, courier_id = splitext(basename(filename))[0].split('_')
    index: pd.DataFrame = CONFIG.article_index[CONFIG.article_index['courier_id'] == courier_id]
    index_article_ids = {str(x) for x in index.record_number.values}

    assert index_article_ids.issubset(articles.keys())


@pytest.mark.parametrize(
    'file, expected',
    [
        ('tagged_1234_123456.md', 1),
        ('tagged_1952_070990.md', 3),
        ('tagged_1972_052257.md', 0),
    ],
)
def test_issues_have_expected_number_of_unindexed_articles(file, expected):

    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename)

    assert len([x for x in articles.keys() if x.startswith('@')]) == expected, 'Incorrect number of unindexed'


@pytest.mark.parametrize(
    'file, expected',
    [
        ('tagged_1234_123456.md', {'@123456-1'}),
        ('tagged_1952_070990.md', {'@070990-3', '@070990-4', '@070990-5'}),
    ],
)
def test_get_issue_articles_returns_unindexed_articles_with_expected_ids(file, expected):

    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename)

    assert expected.issubset(articles.keys())


@pytest.mark.parametrize(
    'file, article_id, expected',
    [
        ('tagged_1234_123456.md', '@123456-1', 'unindexed article text'),
        ('tagged_1952_070990.md', '@070990-3', 'MARCH) 952 Page 3-UNESCO COURIER'),
        ('tagged_1952_070990.md', '@070990-4', 'UNESCO COURIER-Page 4 MARCH 1952'),
        ('tagged_1952_070990.md', '@070990-5', 'the League who invites all competent persons'),
    ],
)
def test_get_issue_articles_returns_unindexed_articles_with_expected_content(file, article_id, expected):

    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename)

    assert articles[article_id][2].startswith(expected)