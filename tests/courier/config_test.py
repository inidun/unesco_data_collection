import csv
from pathlib import Path

import pytest

from courier.config import get_config

CONFIG = get_config()


def test_config_paths_exists():
    for attr in dir(CONFIG):
        if isinstance(path := getattr(CONFIG, attr), Path):
            assert path.exists()


def test_pdfbox_xml_dir_contains_all_files():
    assert len(list(CONFIG.pdfbox_xml_dir.glob('*.xml'))) == 664


def test_double_pages_returns_correct_for_issues_with_double_pages():
    assert isinstance(CONFIG.double_pages, dict)
    assert CONFIG.double_pages.get('061468', []) == [10, 17]
    assert CONFIG.double_pages.get('069916', []) == [10, 11, 24]
    assert CONFIG.double_pages.get('064331', []) == [18]


def test_double_pages_returns_empty_list_for_excluded_issue():

    with open(CONFIG.exclusions_file, newline='') as fp:
        reader = csv.reader(fp, delimiter=';')
        exclusions = [line[0] for line in reader]

    assert '110425' in exclusions
    assert CONFIG.double_pages.get('110425', []) == []


def test_double_pages_returns_empty_list_for_non_existing_issue():
    assert CONFIG.double_pages.get('0', []) == []


def test_double_pages_returns_default_value_if_set():
    assert CONFIG.double_pages.get('0', [2, 23]) == [2, 23]


def test_double_pages_with_no_default_value_set_returns_expected():
    assert CONFIG.double_pages.get('061468') == [10, 17]
    assert CONFIG.double_pages.get("033144") is None


double_pages_testdata = [
    ('064331', [], [18]),
    ('069916', [], [10, 11, 24]),
    ('069916', [12], [10, 11, 24]),
    ('069916', None, [10, 11, 24]),
    ('110425', [], []),  # issues in exclusions
    ('000000', [], []),
    ('000000', [12], [12]),
    ('000000', None, None),
]


@pytest.mark.parametrize("courier_id,default_value,expected", double_pages_testdata)
def test_double_pages_returns_expected_values(courier_id, default_value, expected):
    result = CONFIG.double_pages.get(courier_id, default_value)
    assert result == expected
