from io import StringIO
from os.path import basename

import pandas as pd
import pytest
from click.testing import CliRunner

from courier.cli.tagged2article import main, verify_extracted
from courier.scripts.tagged_issue_to_articles import load_article_index


def test_CLI_option_help_returns_expected():
    runner = CliRunner()

    result = runner.invoke(main, ['--help'])

    assert result.exit_code == 0
    assert result.output.startswith('Usage: ')


def test_CLI_generates_expected_files(tmp_path):
    file: str = 'tagged_1234_123456.md'
    filepattern: str = f'tests/fixtures/courier/tagged_issue/{file}'

    runner = CliRunner()

    result = runner.invoke(main, [filepattern, str(tmp_path), '--supplements', '--editorials', '--unindexed'])

    assert result.exit_code == 0
    assert len(list(tmp_path.iterdir())) == 6

    output_filenames = [basename(x) for x in tmp_path.iterdir()]
    assert 'info.log' in output_filenames
    assert 'warnings.log' in output_filenames
    assert '1234_123456_78910.txt' in output_filenames
    assert '1234_123456_a123456-1.txt' in output_filenames
    assert '1234_123456_s123456-1.txt' in output_filenames
    assert '1234_123456_e123456-1.txt' in output_filenames


def test_CLI_with_directory_as_input_generates_expected_files(tmp_path):
    expected = {
        'info.log',
        'warnings.log',
        '1234_123456_78910.txt',
        '1234_123456_a123456-1.txt',
        '1234_123456_s123456-1.txt',
        '1234_123456_e123456-1.txt',
        '1952_070990_70992.txt',
        '1952_070990_70995.txt',
        '1952_070990_70996.txt',
        '1952_070990_70997.txt',
        '1952_070990_70999.txt',
        '1952_070990_71001.txt',
        '1952_070990_a070990-3.txt',
        '1952_070990_a070990-4.txt',
        '1952_070990_a070990-5.txt',
        '1972_052257_188090.txt',
        '1972_052257_52256.txt',
        '1972_052257_52341.txt',
        '1972_052257_52342.txt',
        '1972_052257_52343.txt',
        '1972_052257_52344.txt',
        '1972_052257_52354.txt',
        '1972_052257_52357.txt',
        '1978_074803_45931.txt',
        '1978_074803_45935.txt',
        '1978_074803_45967.txt',
        '1978_074803_45968.txt',
        '1978_074803_45970.txt',
        '1978_074803_45973.txt',
        '1978_074803_45974.txt',
        '1978_074803_45975.txt',
        '1978_074803_45978.txt',
        '1978_074803_45981.txt',
        '1978_074803_45983.txt',
        '1978_074803_e074803-4.txt',
        '1978_074803_s074803-36.txt',
        '1978_074803_s074803-37.txt',
        '1978_074803_s074803-38.txt',
        '1978_074803_s074803-39.txt',
    }

    filepattern: str = 'tests/fixtures/courier/tagged_issue/'

    runner = CliRunner()

    result = runner.invoke(main, [filepattern, str(tmp_path), '--supplements', '--editorials', '--unindexed'])

    assert result.exit_code == 0
    assert len(list(tmp_path.iterdir())) == 39
    assert expected == {basename(x) for x in tmp_path.iterdir()}


def test_CLI_using_article_index(tmp_path):
    file: str = 'tagged_1972_052257.md'
    filepattern: str = f'tests/fixtures/courier/tagged_issue/{file}'

    article_index = 'tests/fixtures/courier/tagged_issue/article_index_052257.csv'

    runner = CliRunner()

    result = runner.invoke(
        main, [filepattern, str(tmp_path), article_index, '--no-supplements', '--no-editorials', '--no-unindexed']
    )

    assert result.exit_code == 0

    output_filenames = [basename(x) for x in tmp_path.iterdir()]
    assert len(output_filenames) == 11
    assert len([file for file in output_filenames if file.endswith('.txt')]) == 8
    assert 'info.log' in output_filenames
    assert 'warnings.log' in output_filenames
    assert 'document_index.csv' in output_filenames


def test_verify_extracted_logs_duplicated_record_numbers(caplog, tmp_path):
    filepath: str = 'tests/fixtures/courier/tagged_issue/tagged_1972_052257.md'
    article_index = 'tests/fixtures/courier/tagged_issue/article_index_052257_with_duplicates.csv'

    runner = CliRunner()

    result = runner.invoke(
        main, [filepath, str(tmp_path), article_index, '--no-supplements', '--no-editorials', '--no-unindexed']
    )

    assert result.exit_code == 0

    assert 'ERROR' in caplog.text
    assert caplog.text.count('ERROR') == 1
    assert 'Index error. Duplicated record_numbers: 52344, 188090' in caplog.text


@pytest.fixture(name='article_index_issue_with_mismatching_years')
def fixture_article_index_issue_with_mismatching_years() -> pd.DataFrame:
    csv = StringIO(
        """courier_id;year;record_number;pages;catalogue_title;authors
10000;1999;11000;[1,2,3];Some Title;Some Author - Only one article in issue
20000;1999;21000;[1,2,3];Some Title;Some Author
20000;1999;22000;[1,2,3];Some Title;Some Author
20000;2000;23000;[1,2,3];Some Title;Some Author - Mismatching year"""
    )
    return load_article_index(csv)


def test_verify_extracted_logs_articles_with_mismatching_years(
    tmp_path, article_index_issue_with_mismatching_years, caplog
):
    verify_extracted(tmp_path, article_index_issue_with_mismatching_years)
    assert 'mismatching years: 23000' in caplog.text


def test_verify_extracted_does_not_log_articles_in_issues_with_only_one_article_as_having_mismatching_years(
    tmp_path, article_index_issue_with_mismatching_years, caplog
):
    verify_extracted(tmp_path, article_index_issue_with_mismatching_years)
    assert 'mismatching years: 11000' not in caplog.text
