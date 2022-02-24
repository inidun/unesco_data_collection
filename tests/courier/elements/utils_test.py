from pathlib import Path

import pytest
import untangle

from courier.elements import get_pdf_issue_content, get_xml_issue_content, read_xml
from courier.extract.java_extractor import ExtractedPages


def test_get_pdf_issue_content_return_expected_values():
    content: ExtractedPages = get_pdf_issue_content(courier_id='012656')
    assert isinstance(content, ExtractedPages)
    assert 'SEPTEMBER 1966' in str(content.pages[2])


def test_read_xml_removes_control_chars():
    expected = '\n\\x01 \\x02 \\x03 \\x04 \\x05 \\x06 \\x07 \\x08\n\\x0b \\x0c \\x0e \\x0f \\x10 \\x11 \\x12 \\x13 \\x14 \\x15 \\x16 \\x17 \\x18 \\x19 \\x1a \\x1b \\x1c \\x1d \\x1e \\x1f\n'
    content = read_xml(Path('tests/fixtures/invalid_chars.xml'))

    assert isinstance(content, untangle.Element)
    assert content.content.cdata == expected


def test_get_xml_issue_content_return_expected_values():
    content: ExtractedPages = get_xml_issue_content(courier_id='012656')
    assert isinstance(content, ExtractedPages)
    assert 'SEPTEMBER 1966' in str(content.pages[2])


def test_get_xml_issue_content_with_invalid_id_raises_value_error():
    with pytest.raises(ValueError, match='Not a valid courier id'):
        get_xml_issue_content('0')
    with pytest.raises(ValueError, match='not in article index'):
        get_xml_issue_content('000000')
