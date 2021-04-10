from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import untangle

from courier.config import get_config
from courier.elements import CourierIssue, read_xml
from courier.extract_articles import extract_articles_from_issue

CONFIG = get_config()


def test_pdfbox_xml_dir_contains_all_files():
    assert len(list(Path(CONFIG.pdfbox_xml_dir).glob('*.xml'))) == 664


def test_create_courier_issue():
    issue = CourierIssue("061468")
    assert issue.num_articles == 3
    assert issue.num_pages == 34
    assert issue.double_pages == [10, 17]


def test_courier_issues_has_correct_double_pages():
    issue_1 = CourierIssue('061468')
    issue_2 = CourierIssue('069916')
    issue_3_no_doubles = CourierIssue('125736')
    issue_4_excluded = CourierIssue('110425')

    assert issue_1.double_pages == [10, 17]
    assert issue_2.double_pages == [10, 11, 24]
    assert issue_3_no_doubles.double_pages == []
    assert issue_4_excluded.double_pages == []


def test_extract_article_as_xml():
    courier_issue = CourierIssue("061468")
    with TemporaryDirectory() as output_dir:
        extract_articles_from_issue(courier_issue, "article.xml.jinja", output_dir)
        assert (Path(output_dir) / "xml/061468_01_61469.xml").exists()


# TODO: Mock issue
def test_extract_article_as_txt():
    courier_issue = CourierIssue("061468")
    with TemporaryDirectory() as output_dir:
        extract_articles_from_issue(courier_issue, "article.txt.jinja", output_dir)
        assert len(list(Path(Path(output_dir) / "txt").iterdir())) == 3

        article_1 = Path(output_dir) / "txt/061468_01_61469.txt"
        article_2 = Path(output_dir) / "txt/061468_02_61506.txt"
        article_3 = Path(output_dir) / "txt/061468_03_61504.txt"

        assert article_1.exists()
        assert article_2.exists()
        assert article_3.exists()

        assert article_1.stat().st_size == 4968
        assert article_2.stat().st_size == 7500
        assert article_3.stat().st_size == 13973


def test_read_xml_removes_control_chars():
    expected = "\n\\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08\n\\x0b \\x0c \\x0e \\x0f \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1a \\x1b \\x1c \\x1d \\x1e \\x1f\n"
    element = read_xml(Path("tests/fixtures/invalid_chars.xml"))
    assert isinstance(element, untangle.Element)
    assert element.content.cdata == expected


def test_read_double_data_returns_expected_data():
    pages = CONFIG.double_pages
    assert isinstance(pages, dict)
    assert pages.get("016653") == [18]
    assert pages.get("061468") == [10, 17]
    assert len(pages) == 54
    assert pages.get("033144") is None
    assert pages.get("110425") is None
    assert pages.get("074589") is None


# FIXME: import create_regexp from split_article_pages (Must fix split_article_pages first)
# from courier.split_article_pages import create_regexp


@pytest.mark.skip(reason="Must fix split_article_pages")
def test_create_regexp():
    pass
    # title = "A nice and happy! title.? 77Maybe#"
    # expr = create_regexp(title)
    # assert isinstance(expr, str)
    # assert expr == "[^a-zåäö]+nice[^a-zåäö]+and[^a-zåäö]+happy[^a-zåäö]+title[^a-zåäö]+maybe"


@pytest.mark.skip(reason="Must fix split_article_pages")
def test_find_title():
    pass
    # courier_issue = CourierIssue("074891")
    # title = "drought over africa"
    # expr = create_regexp(title)
    # page_numbers = courier_issue.find_pattern(expr)
    # assert page_numbers is not None


@pytest.mark.skip(reason="Not implemented")
def test_missing_articles_are_from_missing_issues():
    pass
