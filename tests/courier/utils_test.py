from courier.config import get_config
from courier.utils import get_filenames, get_stats

CONFIG = get_config()


def test_get_stats(monkeypatch):
    monkeypatch.setattr(CONFIG, 'pdf_dir', CONFIG.test_files_dir)
    stats = get_stats()
    assert stats['files'] == 1
    assert stats['mean'] == 8
    assert stats['median'] == 8
    assert stats['pages'] == 8


def test_get_filenames_returns_only_files_with_expected_extension(tmp_path):

    pdf_file = tmp_path / 'test.pdf'
    pdf_file.touch()
    txt_file = tmp_path / 'test.txt'
    txt_file.touch()

    assert pdf_file in get_filenames(tmp_path)
    assert txt_file not in get_filenames(tmp_path)
    assert txt_file in get_filenames(tmp_path, 'txt')

    assert get_filenames(txt_file) == []
    assert get_filenames(pdf_file) == get_filenames(tmp_path) == [pdf_file]
