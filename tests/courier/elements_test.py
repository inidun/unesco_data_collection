from pathlib import Path

import pandas as pd
import pytest
import untangle

import courier.elements as elements


def test_read_xml_removes_control_chars():

    expected = '\n\\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08\n\\x0b \\x0c \\x0e \\x0f \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1a \\x1b \\x1c \\x1d \\x1e \\x1f\n'

    element = elements.read_xml(Path('tests/fixtures/invalid_chars.xml'))

    assert isinstance(element, untangle.Element)
    assert element.content.cdata == expected


def test_get_courier_issue_index_return_expected_values():
    assert isinstance(elements.get_issue_index(''), pd.DataFrame)
    assert len(elements.get_issue_index('061468')) == 3


@pytest.mark.parametrize(
    'input_pn, input_text, expected_pn, expected_text',
    [
        (1, 'one', 1, 'one'),
        (2, 'two', 2, 'two'),
        (3, 3, 3, '3'),
    ],
)
def test_create_page(input_pn, input_text, expected_pn, expected_text):

    result = elements.Page(input_pn, input_text)
    assert isinstance(result, elements.Page)

    assert isinstance(result.page_number, int)
    assert result.page_number == expected_pn

    assert isinstance(result.text, str)
    assert result.text == expected_text


def test_create_courier_issue():
    issue = elements.CourierIssue('061468')
    assert issue.num_articles == 3
    assert issue.num_pages == 34
    assert issue.double_pages == [10, 17]


def test_courier_issues_has_correct_double_pages():
    issue_1 = elements.CourierIssue('061468')
    issue_2 = elements.CourierIssue('069916')
    issue_3_no_doubles = elements.CourierIssue('125736')
    issue_4_excluded = elements.CourierIssue('110425')

    assert issue_1.double_pages == [10, 17]
    assert issue_2.double_pages == [10, 11, 24]
    assert issue_3_no_doubles.double_pages == []
    assert issue_4_excluded.double_pages == []


def test_courier_issue_has_correct_index():
    issue_1 = elements.CourierIssue('061468')
    assert not issue_1.issue_index.empty
    assert issue_1.issue_index.size == 24

    issue_2 = elements.CourierIssue('0')
    assert issue_2.issue_index.empty
    assert issue_2.issue_index.size == 0
