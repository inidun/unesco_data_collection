import pytest
import requests

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")


from conventions.convention_parser import ConventionParser
from conventions.convention_parser import ConventionIndexParser

def test_if_test_working():
    assert True


def test_extract__given_a_valid_html__convention_text_retrieved_as_expected():

    # Arrange
    with open("tests/fixtures/sample_response_page.html", "r") as fp:
        page = fp.read()

    # Act
    sut = ConventionParser()
    result = sut.extract(page)

    # Assert
    assert result is not None
    assert len(result) > 0
    assert "Article" in result

def test_extract_text_links__given_a_valid_index_html__returns_list_of_convention_page_urls():

    # http://portal.unesco.org/en/ev.php-URL_ID=12025&URL_DO=DO_TOPIC&URL_SECTION=-471.html

    # Arrange
    with open("./tests/fixtures/sample_response_index_page.html", "r") as fp:
        page = fp.read()

    # Act
    sut = ConventionIndexParser() # returns title, url, date, city, pdfUrl
    result = sut.extract(page)

    # Assert
    assert result is not None
    assert len(result) == 32


