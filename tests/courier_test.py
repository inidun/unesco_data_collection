import os
import tempfile
import untangle

from courier.courier_metadata import create_article_index
from courier.elements import CourierIssue
from courier.extract_articles import create_regexp, extract_articles_from_issue, read_double_pages_from_file, read_xml

TEST_OUTPUT_FOLDER = './tests/output'

# INPUT
# overlapping_pages.csv
XML_INPUT_FOLDER = "data/courier/input/xml"
METADATA_FILE = "data/courier/UNESCO_Courier_metadata.csv"


def test_input_dir_contains_all_files():

    num_files = len([f for f in os.listdir(XML_INPUT_FOLDER) if os.path.isfile(os.path.join(XML_INPUT_FOLDER, f))])

    assert num_files == 664


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


# FIXME: Use tempdir
def test_convert():

    os.makedirs(TEST_OUTPUT_FOLDER, exist_ok=True)

    article_index = create_article_index(METADATA_FILE)
    issue_index = article_index.loc[article_index["courier_id"] == "061468"]
    issue = untangle.parse(os.path.join(XML_INPUT_FOLDER, "061468engo.xml"))
    double_pages = read_double_pages_from_file(
        "data/courier/double_pages/double_pages.txt", "./data/courier/double_pages/exclude.txt"
    )
    courier_issue = CourierIssue(issue_index, issue, double_pages.get("061468", []))

    extract_articles_from_issue(courier_issue, "article.txt.jinja", TEST_OUTPUT_FOLDER)
    extract_articles_from_issue(courier_issue, "article.xml.jinja", TEST_OUTPUT_FOLDER)

    # TODO: Actual tests
    assert os.path.isfile(os.path.join(TEST_OUTPUT_FOLDER, "061468_01_61469.xml"))
    assert True


def test_find_title():

    article_index = create_article_index(METADATA_FILE)

    issue_index = article_index.loc[article_index["courier_id"] == "074891"]
    issue = untangle.parse(os.path.join(XML_INPUT_FOLDER, "074891engo.xml"))
    courier_issue = CourierIssue(issue_index, issue, [])

    title = "drought over africa"
    expr = create_regexp(title)

    page_numbers = courier_issue.find_pattern(expr)

    assert page_numbers is not None


def test_read_xml_removes_control_chars():

    expected = "\n\\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08\n\\x0b \\x0c \\x0e \\x0f \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1a \\x1b \\x1c \\x1d \\x1e \\x1f\n"

    element = read_xml("./tests/fixtures/invalid_chars.xml")

    assert isinstance(element, untangle.Element)
    assert element.content.cdata == expected


def test_read_double_data_returns_expected_data():

    pages = read_double_pages_from_file(
        "data/courier/double_pages/double_pages.txt", "./data/courier/double_pages/exclude.txt"
    )

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


def test_tempfile():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with open(os.path.join(tmpdirname, "tempfile"), "w") as fp:
            fp.write("bleh")
            assert os.path.isfile(os.path.join(tmpdirname, "tempfile"))
        assert os.path.isdir(tmpdirname)
        # print(os.listdir(tmpdirname))

    assert not os.path.isdir(tmpdirname)
