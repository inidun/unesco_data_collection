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
    assert '1234_123456_a123456-1.txt' in [basename(x) for x in tmp_path.iterdir()]
    assert '1234_123456_78910.txt' in [basename(x) for x in tmp_path.iterdir()]


def test_CLI_with_directory_as_input_generates_expected_files(tmp_path):

    expected = {
        '1234_123456_78910.txt',
        '1234_123456_a123456-1.txt',
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
    }

    filepattern: str = 'tests/fixtures/courier/tagged_issue/'

    runner = CliRunner()

    result = runner.invoke(main, [filepattern, str(tmp_path)])

    assert result.exit_code == 0
    assert len(list(tmp_path.iterdir())) == 19
    assert expected == {basename(x) for x in tmp_path.iterdir()}
