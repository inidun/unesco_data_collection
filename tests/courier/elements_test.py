from pathlib import Path

import pytest
import untangle

import courier.elements as elements


def test_read_xml_removes_control_chars():

    expected = '\n\\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08\n\\x0b \\x0c \\x0e \\x0f \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1a \\x1b \\x1c \\x1d \\x1e \\x1f\n'

    element = elements.read_xml(Path('tests/fixtures/invalid_chars.xml'))

    assert isinstance(element, untangle.Element)
    assert element.content.cdata == expected


def test_get_courier_issue_index_return_expected_values():
    assert len(elements.get_issue_index('061468')) == 3


def test_get_courier_issue_index_with_invalid_id_raises_value_error():
    with pytest.raises(ValueError, match='Not a valid courier id'):
        elements.get_issue_index('')
    with pytest.raises(ValueError, match='Not a valid courier id'):
        elements.get_issue_index('0')
    with pytest.raises(ValueError, match='not in article index'):
        elements.get_issue_index('000000')


def test_get_issue_content_return_expected_values():
    courier_issue = elements.CourierIssue('061468')
    assert isinstance(courier_issue.content, untangle.Element)
    assert 'MARCH 1964' in courier_issue.content.document.page[2].cdata


def test_get_issue_content_with_invalid_id_raises_value_error():
    with pytest.raises(ValueError, match='Not a valid courier id'):
        elements.get_issue_content('0')
    with pytest.raises(ValueError, match='not in article index'):
        elements.get_issue_content('000000')


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
    courier_issue = elements.CourierIssue('061468')
    assert isinstance(courier_issue, elements.CourierIssue)

    assert courier_issue.num_articles == 3
    assert courier_issue.num_pages == 34
    assert courier_issue.double_pages == [10, 17]


def test_create_non_existing_issue_raises_value_error():
    with pytest.raises(ValueError, match='Not a valid courier id'):
        elements.get_issue_content('0')
    with pytest.raises(ValueError, match='not in article index'):
        elements.CourierIssue('000000')


@pytest.mark.parametrize(
    'courier_id, expected',
    [
        ('061468', [10, 17]),
        ('069916', [10, 11, 24]),
        ('125736', []), # no double pages
        ('110425', []), # excluded
    ],
)
def test_courier_issues_has_correct_double_pages(courier_id, expected):
    result = elements.CourierIssue(courier_id).double_pages
    assert result == expected

def test_courier_issue_has_correct_index():
    issue_1 = elements.CourierIssue('061468')
    assert not issue_1.index.empty
    assert issue_1.index.size == 24
