import pytest

from courier.config import get_config
from courier.utils import corrected_page_number, flatten, pdf_stats

CONFIG = get_config()


def test_flatten_returns_expected_values():
    assert flatten([[1, 2, 3], (4, 5, 6), [7, 8]]) == [1, 2, 3, 4, 5, 6, 7, 8]
    assert flatten((('a', 'b'), [1, 2])) == ['a', 'b', 1, 2]


def test_pdf_stats(monkeypatch):
    monkeypatch.setattr(CONFIG, 'pdf_dir', CONFIG.test_files_dir)
    stats = pdf_stats()
    assert stats['files'] == 1
    assert stats['mean'] == 8
    assert stats['median'] == 8
    assert stats['pages'] == 8


@pytest.mark.parametrize(
    'courier_id, page_number, expected',
    [
        ('012656', 10, 10),
        ('012656', 20, 19),
        ('069916', 25, 22),
        ('033144', 65, 65),
    ],
)
def test_corrected_page_number_returns_expected(courier_id, page_number, expected):
    result = corrected_page_number(courier_id, page_number)
    assert result == expected
