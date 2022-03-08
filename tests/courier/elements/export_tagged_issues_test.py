from pathlib import Path

import pytest

from courier.config import get_config
from courier.elements import CourierIssue
from courier.elements.export_tagged_issues import export_tagged_issue

CONFIG = get_config()


@pytest.mark.skip(reason='Patched config')
def test_pdf_has_correct_number_of_titles(monkeypatch):
    monkeypatch.setattr(CONFIG, 'pdf_dir', Path('tests/fixtures/courier/custom_pdf'))
    monkeypatch.setattr(CONFIG, 'metadata_file', Path('tests/fixtures/courier/custom_pdf/metadata.csv'))

    courier_id = '012356'
    issue: CourierIssue = CourierIssue(courier_id)

    assert [len(x.titles) for x in issue.pages] == [3, 3, 1]


@pytest.mark.skip(reason='Patched config')
def test_export_tagged(monkeypatch, tmp_path):
    monkeypatch.setattr(CONFIG, 'pdf_dir', Path('tests/fixtures/courier/custom_pdf'))
    monkeypatch.setattr(CONFIG, 'metadata_file', Path('tests/fixtures/courier/custom_pdf/metadata.csv'))

    courier_id = '012356'

    export_tagged_issue(courier_id=courier_id, export_folder=tmp_path)

    assert (tmp_path / f'tagged_2022_{courier_id}.md').exists()
