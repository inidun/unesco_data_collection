from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from courier.config import get_config
from courier.elements import CourierIssue
from courier.extract_articles import extract_articles_from_issue

CONFIG = get_config()


def test_extract_article_as_xml():
    courier_issue = CourierIssue('061468')
    with TemporaryDirectory() as output_dir:
        extract_articles_from_issue(courier_issue, 'article.xml.jinja', output_dir)
        assert (Path(output_dir) / 'xml/061468_01_61469.xml').exists()


# TODO: Mock issue
def test_extract_article_as_txt():
    courier_issue = CourierIssue('061468')
    with TemporaryDirectory() as output_dir:
        extract_articles_from_issue(courier_issue, 'article.txt.jinja', output_dir)
        assert len(list(Path(Path(output_dir) / 'txt').iterdir())) == 3

        article_1 = Path(output_dir) / 'txt/061468_01_61469.txt'
        article_2 = Path(output_dir) / 'txt/061468_02_61506.txt'
        article_3 = Path(output_dir) / 'txt/061468_03_61504.txt'

        assert article_1.exists()
        assert article_2.exists()
        assert article_3.exists()

        assert article_1.stat().st_size == 4968
        assert article_2.stat().st_size == 7500
        assert article_3.stat().st_size == 13973


# FIXME: import create_regexp from split_article_pages (Must fix split_article_pages first)
# from courier.split_article_pages import create_regexp


@pytest.mark.skip(reason='Must fix split_article_pages')
def test_create_regexp():
    pass
    # title = 'A nice and happy! title.? 77Maybe#'
    # expr = create_regexp(title)
    # assert isinstance(expr, str)
    # assert expr == '[^a-zåäö]+nice[^a-zåäö]+and[^a-zåäö]+happy[^a-zåäö]+title[^a-zåäö]+maybe'


@pytest.mark.skip(reason='Must fix split_article_pages')
def test_find_title():
    pass
    # courier_issue = CourierIssue('074891')
    # title = 'drought over africa'
    # expr = create_regexp(title)
    # page_numbers = courier_issue.find_pattern(expr)
    # assert page_numbers is not None


@pytest.mark.skip(reason='Not implemented')
def test_missing_articles_are_from_missing_issues():
    pass
