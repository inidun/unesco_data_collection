from courier.extract_articles import extract_articles, extract_articles_from_issue
import untangle
from courier.elements import CourierIssue
from courier.courier_metadata import create_article_index
from courier.extract_articles import read_xml


def test_extract():
    # Arrange
    article_index = create_article_index("./courier/UNESCO_Courier_metadata.csv")
    article_index = article_index.loc[article_index["courier_id"] == "012656"]
    issue = untangle.parse("./data/courier/xml/012656engo.xml")
    courier_issue = CourierIssue(article_index, issue)

    # Act
    article = next(courier_issue.articles)
    page = next(article.pages)

    # Assert
    assert courier_issue is not None
    assert page is not None


def test_convert():
    article_index = create_article_index("./courier/UNESCO_Courier_metadata.csv")
    article_index = article_index.loc[article_index["courier_id"] == "012656"]
    issue = untangle.parse("./data/courier/xml/012656engo.xml")
    courier_issue = CourierIssue(article_index, issue)

    articles = extract_articles_from_issue(courier_issue)

    with open("test.xml", "w") as fp:
        fp.write(articles[0])

    assert articles is not None
    # TODO: assert correct


def test_find_title():
    article_index = create_article_index("./courier/UNESCO_Courier_metadata.csv")
    article_index = article_index.loc[article_index["courier_id"] == "012656"]
    issue = untangle.parse("./data/courier/xml/012656engo.xml")
    courier_issue = CourierIssue(article_index, issue)

    title = "The Years of the quiet sun"
    # TODO: Fix whitespaces
    expr = title.lower().replace(" ", r"\s+")
    page_numbers = courier_issue.find_pattern(expr)

    assert page_numbers is not None


def test_remove_control_chars():
    element = read_xml("./data/courier/xml/125736eng.xml")
   
    assert element is not None


# test rätt antal artiklar
# rätt antal sidor
# test output OK

# --> csv
# record number, title,
