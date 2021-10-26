import filecmp
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from courier.config import get_config
from courier.elements import CourierIssue, IssueStatistics, export_articles

CONFIG = get_config()


def test_export_articles_generates_expected_output():
    with TemporaryDirectory() as output_dir:
        errors = export_articles('012656', output_dir)
        assert len(sorted(Path(output_dir).glob('*.txt'))) == 5
        assert filecmp.dircmp(output_dir, CONFIG.test_files_dir / 'expected/export_articles').diff_files == []
        assert len(filecmp.dircmp(output_dir, CONFIG.test_files_dir / 'not_expected').diff_files) == 1
        assert len(errors) == 0


def test_export_articles_with_errors_generates_expected_output():
    courier_id = '063436'
    issue = CourierIssue(courier_id)
    with TemporaryDirectory() as output_dir:
        errors = export_articles('063436', output_dir)
        assert len(sorted(Path(output_dir).glob('*.txt'))) == IssueStatistics(issue).number_of_articles
        assert len(errors) != 0


def test_stats():
    courier_ids = ['066943', '014255', '016653']
    stats = []

    with TemporaryDirectory() as output_dir:
        for courier_id in courier_ids:
            stats += export_articles(courier_id, output_dir)

    statistics = (
        pd.DataFrame(stats)
        .drop(columns=['article'])
        .sort_values(by=['year', 'courier_id', 'record_number', 'page', 'case'])
    )
    assert statistics is not None
