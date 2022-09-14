from os.path import basename

from click.testing import CliRunner

from courier.cli.tagged2article import main


def test_CLI_option_help_returns_expected():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert result.output.startswith('Usage: ')


def test_CLI_generates_expected_files(tmp_path):

    file: str = 'tagged_1234_123456.md'
    filepattern: str = f'tests/fixtures/courier/tagged_issue/{file}'

    runner = CliRunner()
    result = runner.invoke(main, [filepattern, str(tmp_path)])
    assert result.exit_code == 0
    assert len(list(tmp_path.iterdir())) == 2

    assert '1234_123456_@123456-1.txt' in [basename(x) for x in tmp_path.iterdir()]
    assert '1234_123456_78910.txt' in [basename(x) for x in tmp_path.iterdir()]
