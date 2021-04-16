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


def test_get_filenames_only_returns_pdf_files(tmp_path):
    tempdir = tmp_path / 'files'
    tempdir.mkdir()
    pdf_file = tempdir / 'test.pdf'
    txt_file = tempdir / 'test.txt'
    pdf_file.touch()
    txt_file.touch()
    assert len(list(tempdir.iterdir())) == 2
    assert pdf_file in list(tempdir.iterdir())
    assert txt_file in list(tempdir.iterdir())
    assert len(get_filenames(tempdir)) == 1
    assert pdf_file in get_filenames(tempdir)
    assert txt_file not in get_filenames(tempdir)
    assert get_filenames(txt_file) == []
    assert get_filenames(pdf_file) == [pdf_file]
