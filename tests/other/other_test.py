import os
import tempfile
from pathlib import Path

from courier.config import CourierConfig

config = CourierConfig()


def test_tempfile():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with open(os.path.join(tmpdirname, "tempfile"), "w") as fp:
            fp.write("bleh")
            assert os.path.isfile(os.path.join(tmpdirname, "tempfile"))
        assert os.path.isdir(tmpdirname)
        # print(os.listdir(tmpdirname))

    assert not os.path.isdir(tmpdirname)


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


def test_config_double_pages_returns_dict():
    assert isinstance(config.double_pages, dict)
    assert config.double_pages.get("061468", []) == [10, 17]
