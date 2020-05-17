import requests
import sys
import os
#import sure
import httpretty

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

import src.legal_instruments.extract as parser
import src.legal_instruments.tasks as task

from src.legal_instruments.pipeline import Pipeline

def project_root():
    folder = os.getcwd()
    while os.path.split(folder)[1] not in ('', 'unesco_data_collection'):
        folder, _ = os.path.split(folder)
    return folder

def get_sample_convention_html():
    with open("{}/src/tests/fixtures/sample_response_page.html".format(project_root()), "r") as fp:
        return fp.read()

def get_sample_convention_index_html():
    with open("{}/src/tests/fixtures/sample_response_index_page.html".format(project_root()), "r") as fp:
        return fp.read()

def test_if_test_working():
    assert True

def test_extract_where_and_when_with_city_succeeds():

    info = "Paris, 13 November 2017"
    where_and_when = parser.extract_where_and_when(info)

    assert where_and_when.year == 2017
    assert where_and_when.month == 11
    assert where_and_when.day == 13
    assert where_and_when.city == "Paris"

def test_extract_where_and_when_without_city_succeeds():

    info = "13 November 2017"
    where_and_when = parser.extract_where_and_when(info)

    assert where_and_when.year == 2017
    assert where_and_when.month == 11
    assert where_and_when.day == 13
    assert where_and_when.city == ""

def test_extract_text_when_valid_page_returns_text():

    # Arrange
    page = get_sample_convention_html()

    # Act
    result = parser.extract_text(page)

    # Assert
    assert result is not None
    assert len(result) > 0
    assert "Article" in result

def test_extract_links_when_valid_page_returns_links():

    # http://portal.unesco.org/en/ev.php-URL_ID=12025&URL_DO=DO_TOPIC&URL_SECTION=-471.html

    # Arrange
    page = get_sample_convention_index_html()

    # Act
    result = list(parser.extract_links(page, "DUMMY"))

    # Assert
    assert result is not None
    assert len(result) == 32

@httpretty.activate
def test_can_mock_http_request():

    # Arrange
    url = "http://portal.unesco.org/en/ev.php-URL_ID=12025&URL_DO=DO_TOPIC&URL_SECTION=-471.html"
    body = get_sample_convention_index_html()
    httpretty.register_uri(httpretty.GET, url, body=body)

    # Act
    response = requests.get(url)

    #Asserts
    assert response.content.decode() == body

@httpretty.activate
def test_pipeline():

    # Arrange
    url_index = "http://index.dumma.du"
    url_text = "http://text.dumma.du"

    httpretty.register_uri(httpretty.GET, url_index, body=get_sample_convention_index_html())
    httpretty.register_uri(httpretty.GET, url_text, body=get_sample_convention_html())
    httpretty.enable()

    def spoof_url(items):
        for x in items:
            x.href = url_text
            yield x

    # Act
    pipeline = Pipeline()\
        .add(task.scrape_pages)\
        .add(task.extract_links)\
        .add(spoof_url)\
        .add(task.extract_text)\
        .add(task.progress)\
        .add(task.store_text, "legal_instruments_corpus.txt.zip")\
        .add(task.store_index, "legal_instruments_index.csv")

    result = pipeline.apply([(url_index, 'CONVENTION')])

    # Assert
    result = list(result)

    assert result is not None
