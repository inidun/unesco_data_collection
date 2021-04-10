from pathlib import Path

from courier.config import CourierConfig

config = CourierConfig()


def test_config_paths_exists():
    assert Path(config.base_data_dir).exists()
    assert Path(config.pdf_dir).exists()
    assert Path(config.pdfbox_txt_dir).exists()
    assert Path(config.pdfbox_xml_dir).exists()
    assert Path(config.tessseract_output_dir).exists()
    assert Path(config.default_output_dir).exists()
    assert Path(config.test_files_dir).exists()

    assert Path(config.project_root).exists()
    assert Path(config.test_output_dir).exists()

    assert Path(config.double_pages_file).exists()
    assert Path(config.overlapping_pages).exists()
    assert Path(config.exclusions_file).exists()
    assert Path(config.courier_metadata).exists()


def test_double_pages_returns_correct_for_issues_with_double_pages():
    assert config.double_pages.get('061468', []) == [10, 17]
    assert config.double_pages.get('069916', []) == [10, 11, 24]
    assert config.double_pages.get('064331', []) == [18]


def test_double_pages_returns_empty_list_for_excluded_issue():
    assert isinstance(config.double_pages, dict)
    assert config.double_pages.get('110425', []) == []  # in excluded files


def test_double_pages_returns_empty_list_for_non_existing_issue():
    assert config.double_pages.get('0', []) == []


def test_double_pages_returns_default_value_if_set():
    assert config.double_pages.get('0', [2, 23]) == [2, 23]
