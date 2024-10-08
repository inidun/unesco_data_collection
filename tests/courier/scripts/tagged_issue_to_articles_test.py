from io import StringIO
from os.path import basename, splitext

import pandas as pd
import pytest

from courier.config import get_config
from courier.scripts.tagged_issue_to_articles import get_issue_articles, load_article_index, verify_articles

CONFIG = get_config()


def test_get_issue_articles_returns_expected():
    filename = 'tests/fixtures/courier/tagged_issue/tagged_1234_123456.md'

    articles = get_issue_articles(
        filename, extract_editorials=True, extract_supplements=True, extract_unindexed_articles=True
    )

    assert len(articles) == 4

    assert '78910' in articles.keys()
    assert articles['78910'][2].startswith('article text')

    assert len([x for x in articles.keys() if x.startswith('a')]) == 1
    assert 'a123456-1' in articles.keys()
    assert articles['a123456-1'][2].startswith('unindexed article text')

    assert len([x for x in articles.keys() if x.startswith('s')]) == 1
    assert 's123456-1' in articles.keys()
    assert articles['s123456-1'][2].startswith('unindexed supplement text')

    assert len([x for x in articles.keys() if x.startswith('e')]) == 1
    assert 'e123456-1' in articles.keys()
    assert articles['e123456-1'][2].startswith('editorial text')


@pytest.mark.parametrize(
    'file',
    [('tagged_1952_070990.md'), ('tagged_1972_052257.md'), ('tagged_1978_074803.md')],
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
        ('tagged_1978_074803.md', 0),
    ],
)
def test_issues_have_expected_number_of_unindexed_articles(file, expected):
    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename, extract_unindexed_articles=True)

    assert len([x for x in articles.keys() if x.startswith('a')]) == expected, 'Incorrect number of unindexed articles'


@pytest.mark.parametrize(
    'file, expected',
    [
        ('tagged_1234_123456.md', {'a123456-1'}),
        ('tagged_1952_070990.md', {'a070990-3', 'a070990-4', 'a070990-5'}),
    ],
)
def test_get_issue_articles_returns_unindexed_articles_with_expected_ids(file, expected):
    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename, extract_unindexed_articles=True)

    assert expected.issubset(articles.keys())


@pytest.mark.parametrize(
    'file, article_id, expected',
    [
        ('tagged_1234_123456.md', 'a123456-1', 'unindexed article text'),
        ('tagged_1952_070990.md', 'a070990-3', 'MARCH) 952 Page 3-UNESCO COURIER'),
        ('tagged_1952_070990.md', 'a070990-4', 'UNESCO COURIER-Page 4 MARCH 1952'),
        ('tagged_1952_070990.md', 'a070990-5', 'the League who invites all competent persons'),
    ],
)
def test_get_issue_articles_returns_unindexed_articles_with_expected_content(file, article_id, expected):
    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename, extract_unindexed_articles=True)

    assert articles[article_id][2].startswith(expected)


@pytest.mark.parametrize(
    'file, expected',
    [
        ('tagged_1234_123456.md', 1),
        ('tagged_1952_070990.md', 0),
        ('tagged_1972_052257.md', 0),
        ('tagged_1978_074803.md', 4),
    ],
)
def test_issues_have_expected_number_of_unindexed_supplements(file, expected):
    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename, extract_supplements=True)

    assert len([x for x in articles.keys() if x.startswith('s')]) == expected, 'Incorrect number of unindexed articles'


@pytest.mark.parametrize(
    'file, expected',
    [
        ('tagged_1234_123456.md', {'s123456-1'}),
        ('tagged_1952_070990.md', set()),
        (
            'tagged_1978_074803.md',
            {
                's074803-36',
                's074803-37',
                's074803-38',
                's074803-39',
            },
        ),
    ],
)
def test_get_issue_articles_returns_unindexed_supplements_with_expected_ids(file, expected):
    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename, extract_supplements=True)

    assert expected.issubset(articles.keys())


@pytest.mark.parametrize(
    'file, article_id, expected',
    [
        ('tagged_1234_123456.md', 's123456-1', 'unindexed supplement text'),
        ('tagged_1978_074803.md', 's074803-36', 'MAY 1978'),
        ('tagged_1978_074803.md', 's074803-37', 'Donald Woods'),
        ('tagged_1978_074803.md', 's074803-38', 'Journalists say'),
        ('tagged_1978_074803.md', 's074803-39', 'Unesco Clubs'),
    ],
)
def test_get_issue_articles_returns_unindexed_supplements_with_expected_content(file, article_id, expected):
    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename, extract_supplements=True)

    assert articles[article_id][2].startswith(expected)


@pytest.mark.parametrize(
    'file, expected',
    [
        ('tagged_1234_123456.md', 1),
        ('tagged_1952_070990.md', 0),
        ('tagged_1972_052257.md', 0),
        ('tagged_1978_074803.md', 1),
    ],
)
def test_issues_have_expected_number_of_editorials(file, expected):
    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename, extract_editorials=True)

    assert len([x for x in articles.keys() if x.startswith('e')]) == expected, 'Incorrect number of unindexed articles'


@pytest.mark.parametrize(
    'file, expected',
    [
        ('tagged_1234_123456.md', {'e123456-1'}),
        ('tagged_1952_070990.md', set()),
        ('tagged_1978_074803.md', {'e074803-4'}),
    ],
)
def test_get_issue_articles_returns_editorials_with_expected_ids(file, expected):
    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename, extract_editorials=True)

    assert expected.issubset(articles.keys())


@pytest.mark.parametrize(
    'file, article_id, expected',
    [
        ('tagged_1234_123456.md', 'e123456-1', 'editorial text'),
        ('tagged_1978_074803.md', 'e074803-4', 'In most countries'),
    ],
)
def test_get_issue_articles_returns_editorials_with_expected_content(file, article_id, expected):
    filename = f'tests/fixtures/courier/tagged_issue/{file}'
    articles = get_issue_articles(filename, extract_editorials=True)

    assert articles[article_id][2].startswith(expected)


@pytest.mark.parametrize(
    'issue_file, article_id, article_file',
    [
        ('tagged_1972_052257.md', '52256', '52256.txt'),
    ],
)
def test_extracted_article_text_is_as_expected(issue_file, article_id, article_file):
    tagged_issue = f'tests/fixtures/courier/tagged_issue/{issue_file}'
    articles = get_issue_articles(tagged_issue)
    article_text = articles[article_id][2]

    with open(f'tests/fixtures/courier/articles_from_tagged/{article_file}', encoding='utf-8', mode='r') as fp:
        expected = fp.read()

    assert article_text == expected


def test_load_article_index():
    csv_index = StringIO(
        """courier_id;year;record_number;pages;catalogue_title;authors
90000;1999;10000;[1,2];Some Title; Some Author
90001;2000;10001;[1,3];Other Title; Other Author"""
    )
    article_index = load_article_index(csv_index)

    assert all(
        article_index.columns
        == ['courier_id', 'year', 'record_number', 'pages', 'catalogue_title', 'authors', 'filename']
    )
    assert article_index.dtypes.to_list() == ['int64', 'int64', 'int64', 'O', 'O', 'O', 'O']
    assert article_index.index.name == 'document_id'


def test_load_article_index_from_xlsx():
    xlsx_index = 'tests/fixtures/courier/tagged_issue/minimal_excel_article_index.xlsx'
    article_index = load_article_index(xlsx_index)

    assert all(
        article_index.columns
        == ['courier_id', 'year', 'record_number', 'pages', 'catalogue_title', 'authors', 'filename']
    )
    assert article_index.dtypes.to_list() == ['int64', 'int64', 'int64', 'O', 'O', 'O', 'O']
    assert article_index.index.name == 'document_id'


@pytest.fixture(name='minimal_article_index')
def fixture_article_index() -> pd.DataFrame:
    csv = StringIO(
        """courier_id;year;record_number;pages;catalogue_title;authors
90000;1999;10000;[1,2];Some Title; Some Author"""
    )
    return load_article_index(csv)


def test_verify_articles_logs_incorrect_record_numbers(minimal_article_index, caplog):
    articles = {'20000': ('20000', [1, 2], 'text')}

    verify_articles(articles, minimal_article_index)

    assert len(caplog.messages)
    assert 'ERROR' in caplog.text
    assert 'Record number not in article index' in caplog.text


def test_verify_articles_logs_incorrect_page_numbers(minimal_article_index, caplog):
    articles = {'10000': ('10000', [1, 2, 3], 'text')}

    verify_articles(articles, minimal_article_index)

    assert len(caplog.messages)
    assert 'ERROR' in caplog.text
    assert 'Page mismatch' in caplog.text


@pytest.fixture(name='corrupt_article_index')
def fixture_corrupt_article_index() -> pd.DataFrame:
    csv = StringIO(
        """courier_id;year;record_number;pages;catalogue_title;authors
90000;1999;10000;[1,2, ,3];Some Title;Some Author"""
    )
    return load_article_index(csv)


def test_verify_articles_logs_articles_with_invalid_page_numbers(corrupt_article_index, caplog):
    articles = {'10000': ('10000', [1, 2], 'text')}

    verify_articles(articles, corrupt_article_index)

    assert len(caplog.messages)
    assert 'ERROR' in caplog.text
    assert 'Invalid page numbers' in caplog.text
