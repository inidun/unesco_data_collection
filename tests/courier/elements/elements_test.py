from typing import Optional

import pytest

from courier.config import get_config
from courier.elements import Article, CourierIssue, DoubleSpreadRightPage, Page
from courier.elements.elements import ExtractionError

CONFIG = get_config()


def test_create_ExtractionError():
    courier_issue: CourierIssue = CourierIssue('012656')
    article: Optional[Article] = courier_issue.get_article(15043)
    assert article is not None
    extraction_error = ExtractionError(article, page=1, case=2)
    assert extraction_error is not None


@pytest.mark.parametrize(
    'input_pn, input_text, expected_pn, expected_text',
    [
        (1, 'one', 1, 'one'),
        (2, 'two', 2, 'two'),
        (3, 3, 3, '3'),
    ],
)
def test_create_page(input_pn, input_text, expected_pn, expected_text):

    result = Page(input_pn, input_text)
    assert isinstance(result, Page)

    assert isinstance(result.page_number, int)
    assert result.page_number == expected_pn

    assert isinstance(result.text, str)
    assert result.text == expected_text


def test_page_str_returns_expected():
    page = Page(page_number=1, text='test string')
    assert str(page) == 'test string'


def test_create_article():
    courier_issue: CourierIssue = CourierIssue('012656')
    assert courier_issue.courier_id == '012656'
    assert courier_issue.num_articles == 5
    assert len(courier_issue) == 36
    assert courier_issue.double_pages == [18]
    article: Optional[Article] = courier_issue.get_article(61469)
    assert article is None
    article: Optional[Article] = courier_issue.get_article(15043)
    assert article is not None
    assert article.catalogue_title == 'Bronze miniatures from ancient Sardinia'
    assert article.year == 1966


def test_create_courier_issue():
    courier_issue = CourierIssue('061468')
    assert isinstance(courier_issue, CourierIssue)

    assert len(courier_issue) == 36
    assert courier_issue.num_articles == 3
    assert courier_issue.double_pages == [10, 18]


def test_create_non_existing_issue_raises_value_error():
    with pytest.raises(ValueError, match='Not a valid courier id'):
        CourierIssue('0')
    with pytest.raises(ValueError, match='not in article index'):
        CourierIssue('000000')


@pytest.mark.parametrize(
    'courier_id, expected',
    [
        ('061468', [10, 18]),  # 10, 17 in PDF
        ('069916', [10, 12, 26]),  # 10, 11, 24 in PDF
        ('125736', []),  # no double pages
        ('110425', []),  # excluded
    ],
)
def test_courier_issues_has_correct_double_pages(courier_id, expected):
    result = CourierIssue(courier_id).double_pages
    assert result == expected


def test_courier_issue_get_page_when_issue_has_double_pages_returns_expected():
    courier_issue = CourierIssue('069916')
    assert courier_issue._pdf_double_page_numbers == [10, 11, 24]  # pylint: disable=protected-access
    assert courier_issue.double_pages == [10, 12, 26]

    assert courier_issue.get_page(11) == courier_issue.__getitem__(10) == courier_issue[10]

    assert isinstance(courier_issue.get_page(11), DoubleSpreadRightPage)
    assert isinstance(courier_issue.get_page(13), DoubleSpreadRightPage)
    assert isinstance(courier_issue.get_page(27), DoubleSpreadRightPage)

    assert courier_issue.get_page(11).text == courier_issue.get_page(13).text == courier_issue.get_page(27).text == ''


@pytest.mark.parametrize(
    'courier_id, page_number, expected',
    [
        ('012656', 15, 14),
        ('012656', 18, 17),
        ('012656', 19, 17),
        ('012656', 20, 18),
        ('012656', 21, 19),
        ('069916', 10, 9),
        ('069916', 11, 9),
        ('069916', 12, 10),
        ('069916', 26, 23),
        ('069916', 27, 23),
    ],
)
def test_to_pdf_page_number_returns_expected(courier_id, page_number, expected):
    issue = CourierIssue(courier_id)
    result = issue.to_pdf_page_number(page_number)
    assert result == expected
