from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import untangle

from courier.config import CourierConfig
from courier.elements import CourierIssue, read_xml
from courier.extract_articles import create_regexp, extract_articles_from_issue

# FIXME: import create_regexp from split_article_pages (Must fix split_article_pages first)
# from courier.split_article_pages import create_regexp

CONFIG = CourierConfig()


# @pytest.fixture(name="article_index")
# def fixture_article_index() -> pd.DataFrame:
#    return create_article_index(CONFIG.courier_metadata)


def test_pdfbox_xml_dir_contains_all_files():
    assert len(list(Path(CONFIG.pdfbox_xml_dir).glob('*.xml'))) == 664


def test_create_courier_issue():
    issue = CourierIssue("061468")
    assert issue.num_articles == 3
    assert issue.num_pages == 34
    assert issue.double_pages == [10, 17]


def test_extract_article_as_xml():
    courier_issue = CourierIssue("061468")
    with TemporaryDirectory() as output_dir:
        extract_articles_from_issue(courier_issue, "article.xml.jinja", output_dir)
        assert (Path(output_dir) / "xml/061468_01_61469.xml").exists()


# Mock issue
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


def test_find_title():
    courier_issue = CourierIssue("074891")
    title = "drought over africa"
    expr = create_regexp(title)
    page_numbers = courier_issue.find_pattern(expr)
    assert page_numbers is not None


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


def test_create_regexp():
    title = "A nice and happy! title.? 77Maybe#"
    expr = create_regexp(title)
    assert isinstance(expr, str)
    assert expr == "[^a-zåäö]+nice[^a-zåäö]+and[^a-zåäö]+happy[^a-zåäö]+title[^a-zåäö]+maybe"


@pytest.mark.skip(reason="Not implemented")
def test_missing_articles_are_from_missing_issues():
    pass


# def test_extract():

#     article_index = create_article_index("./data/courier/UNESCO_Courier_metadata.csv")
#     issue_index = article_index.loc[article_index["courier_id"] == "012656"]
#     issue = untangle.parse("./data/courier/xml/012656engo.xml")
#     double_pages = read_double_pages("./data/courier/double_pages/double_pages.txt")

#     courier_issue = CourierIssue(issue_index, issue, double_pages.get("012656", []))

#     for article in courier_issue.articles:
#         for page in article.pages:
#             assert page is not None

#     assert courier_issue is not None
#     assert page is not None
