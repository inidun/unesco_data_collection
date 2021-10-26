import filecmp
from pathlib import Path
from tempfile import TemporaryDirectory

from courier.config import get_config
from courier.elements import export_articles

CONFIG = get_config()


def test_export_articles_generates_expected_output():
    with TemporaryDirectory() as output_dir:
        errors = export_articles('012656', output_dir)
        assert len(sorted(Path(output_dir).glob('*.txt'))) == 5
        assert filecmp.dircmp(output_dir, CONFIG.test_files_dir / 'expected/export_articles').diff_files == []
        assert len(filecmp.dircmp(output_dir, CONFIG.test_files_dir / 'not_expected').diff_files) == 1
        assert errors is not None
