# pylint: disable=redefined-outer-name
import filecmp
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest

from courier.config import get_config
from courier.elements import CourierIssue, IssueStatistics, export_articles
from courier.elements.export_articles import display_extract_percentage, save_overlap

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


@pytest.fixture
def statistics():
    statistics = StringIO(
        """year;courier_id;record_number;page;case;error;title;comment
2000;111111;73655;6;1;case 1;Title A
2000;222222;73788;8;1;case 1;Title B
2000;222222;74502;2;1;case 1;Title C
2000;333333;73654;1;5;case 5;Title D
2000;333333;73655;1;5;case 5;Title E
2000;333333;73657;2;5;case 5;Title F
2000;333333;73658;2;5;case 5;Title G
2000;333333;73659;2;5;case 5;Title H
2000;444444;73791;6;1;case 1;Title I
2000;444444;73792;6;2;case 2;Title J
"""
    )
    return pd.read_csv(statistics, sep=';')


@pytest.fixture
def overlap_with_cases():
    overlap = StringIO(
        """courier_id;page;count;cases
111111;6;1;1
222222;2;1;1
222222;8;1;1
333333;1;2;5,5
333333;2;3;5,5,5
444444;6;2;1,2
"""
    )
    return pd.read_csv(overlap, sep=';')


def test_save_overlap(statistics, overlap_with_cases):
    overlap = save_overlap(statistics)
    assert all(overlap.columns == ['courier_id', 'page', 'count', 'cases'])
    assert overlap.equals(overlap_with_cases)


@pytest.fixture
def overlap_file():
    return StringIO(
        """courier_id;page;count
111111;6;1
222222;2;1
222222;8;1
333333;1;2
333333;2;3
444444;6;1
555555;1;1
"""
    )


@pytest.mark.skip(reason='Incomplete')
def test_diffs(overlap_file, overlap_with_cases):
    initial_overlap = pd.read_csv(overlap_file, sep=';', index_col=False, encoding='utf-8')
    assert initial_overlap is not None
    assert overlap_with_cases is not None
