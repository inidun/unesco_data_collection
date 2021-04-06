from pathlib import Path

import pytest

from courier.config import CourierConfig
from courier.utils import flatten

config = CourierConfig()


def test_config_paths_exists():
    assert Path(config.base_data_dir).exists()
    assert Path(config.pdf_dir).exists()
    assert Path(config.pdfbox_txt_dir).exists()
    assert Path(config.pdfbox_xml_dir).exists()
    assert Path(config.default_output_dir).exists()
    assert Path(config.project_root).exists()
    assert Path(config.test_output_dir).exists()

    assert Path(config.courier_metadata).exists()
    assert Path(config.double_pages_file).exists()
    assert Path(config.exclusions_file).exists()
    assert Path(config.overlapping_pages).exists()


def test_utils_flatten_returns_expected_values():
    assert flatten([[1, 2, 3], (4, 5, 6), [7, 8]]) == [1, 2, 3, 4, 5, 6, 7, 8]
    assert flatten((('a', 'b'), [1, 2])) == ['a', 'b', 1, 2]


@pytest.mark.skip(reason="Deprecated")
def test_config_double_pages_returns_correct_pages():
    assert isinstance(config.double_pages, dict)
    assert config.double_pages.get("061468", []) == [10, 17]
    assert config.double_pages.get("069916", []) == [10, 11, 24]
    assert config.double_pages.get("064331", []) == [18]
    assert config.double_pages.get("0", []) == []
