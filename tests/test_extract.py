import re

import untangle
from courier.courier_metadata import create_article_index
from courier.elements import CourierIssue
from courier.extract_articles import (extract_articles,
                                      extract_articles_from_issue, read_landscape_pages, read_xml)


def test_extract():
    # Arrange
    article_index = create_article_index("./courier/UNESCO_Courier_metadata.csv")
    article_index = article_index.loc[article_index["courier_id"] == "012656"]
    issue = untangle.parse("./data/courier/xml/012656engo.xml")
    landscape_pages = read_landscape_pages("./courier/landscape_pages.txt")

    courier_issue = CourierIssue(article_index, issue, landscape_pages.get("012656", []))

    # Act
    for article in courier_issue.articles:
        for page in article.pages:
            assert page is not None

    # Assert
    assert courier_issue is not None
    assert page is not None

# FIXME: fix test
def test_convert():
    article_index = create_article_index("./courier/UNESCO_Courier_metadata.csv")
    article_index = article_index.loc[article_index["courier_id"] == "012656"]
    issue = untangle.parse("./data/courier/xml/012656engo.xml")
    courier_issue = CourierIssue(article_index, issue, [])

    articles = extract_articles_from_issue(courier_issue)

    with open("test.xml", "w") as fp:
        fp.write(articles[0])

    assert articles is not None
    # TODO: assert correct


def test_find_title():
    article_index = create_article_index("./courier/UNESCO_Courier_metadata.csv")
    article_index = article_index.loc[article_index["courier_id"] == "074891"]
    issue = untangle.parse("./data/courier/xml/074891engo.xml")
    courier_issue = CourierIssue(article_index, issue, [])

    title = "drought over africa"
    expr = title.lower().replace(" ", "SPACE")            
    #expr = re.escape(expr)
    expr = re.sub(r"[+-\\*,.\\:;\"\']", "\\.?", expr)
    expr = expr.replace("SPACE", " ")
    expr = re.sub(r"\d[\d\s]+\d", r"DIGIT", expr)   
    expr = re.sub(r"\s+", "\\\\s+", expr)
    expr = re.sub("DIGIT", r"\\\\d[\\\\d\\\\s]+\\\\d", expr)

    page_numbers = courier_issue.find_pattern(expr)

    assert page_numbers is not None


def test_remove_control_chars():
    element = read_xml("./data/courier/xml/125736eng.xml")
   
    assert element is not None

def test_read_lanscape_data():
    data = read_landscape_pages("./courier/file.txt")

    assert data is not None

# test rätt antal artiklar
# rätt antal sidor
# test output OK

# --> csv
# record number, title,
