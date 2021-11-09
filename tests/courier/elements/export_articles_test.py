# pylint: disable=redefined-outer-name
import filecmp
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from courier.config import get_config
from courier.elements import CourierIssue, IssueStatistics, export_articles
from courier.elements.export_articles import display_extract_percentage

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

        statistics['case'] = statistics.case.astype('str')
        assert statistics is not None

        stat_groups = statistics.groupby('case')
        with pd.ExcelWriter(Path(output_dir) / 'stats.xlsx') as writer:  # pylint: disable=abstract-class-instantiated
            for key, _ in stat_groups:
                stat_groups.get_group(key).to_excel(writer, sheet_name=key, index=False)

        assert (Path(output_dir) / 'stats.xlsx').exists()


@pytest.fixture
def extract_log():
    return StringIO(
        """courier_id;year;record_number;assigned;not_found;total
012345;1900;11111;3;0;6
123456;1900;11112;2;0;2"""
    )


def test_display_extract_percentage(extract_log):
    success_ratio = display_extract_percentage(extract_log)
    assert isinstance(success_ratio, float)
    assert success_ratio == 0.5
