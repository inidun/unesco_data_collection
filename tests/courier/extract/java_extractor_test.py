import filecmp
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import pytest

from courier.config import get_config
from courier.elements import get_best_candidate
from courier.extract.interface import ITextExtractor
from courier.extract.java_extractor import ExtractedPages, JavaExtractor, get_pdfbox_path
from courier.extract.utils import get_filenames

CONFIG = get_config()


def test_get_pdfbox_path_returns_valid_path():
    assert get_pdfbox_path().exists()


@pytest.mark.java
def test_java_extractor():
    extractor: JavaExtractor = JavaExtractor()
    filename = CONFIG.pdf_dir / '012656engo.pdf'
    issue: ExtractedPages = extractor.extract_pages(filename)

    assert len(issue) == 35
    assert issue.pages[1].pdf_page_number == 2
    assert 'TREASURES' in issue.pages[1].content
    assert len(issue.pages[1].titles) == 2
    assert len([title for title, _ in issue.pages[1].titles if 'TREASURE' in title]) != 0


# TODO: Parametrize
@pytest.mark.java
def test_titles_on_correct_pages():
    extractor: JavaExtractor = JavaExtractor()
    filename = CONFIG.pdf_dir / '012656engo.pdf'
    issue: ExtractedPages = extractor.extract_pages(filename)

    assert titles_in_content(issue)


def titles_in_content(issue: ExtractedPages) -> bool:
    """Returns true iff for each page in `issue` all of the page's titles are contained within the page's content"""
    # pylint: disable=use-a-generator
    return all(
        [
            all([title in issue.pages[i].content for title in [title for title, _ in issue.pages[i].titles]])
            for i in range(0, len(issue))
        ]
    )


# FIXME: Compare with pdfbox extract
@pytest.mark.java
def test_extract_issue_returns_expected_content():
    extractor: JavaExtractor = JavaExtractor()
    filename = CONFIG.pdf_dir / '012656engo.pdf'
    issue: ExtractedPages = extractor.extract_pages(filename)

    p = issue.pages[2].content
    with open(CONFIG.pages_dir / 'pdfbox/012656engo_0003.txt', 'r', encoding='utf-8') as fp:
        text = fp.read().strip()

    assert p == text


# TODO: Add more test cases
@pytest.mark.parametrize(
    'filename, title, page_number',
    [
        (CONFIG.pdf_dir / '077050engo.pdf', 'The Rubber man', 34),
        (CONFIG.pdf_dir / '068057engo.pdf', 'Where the sky is black', 28),
        (CONFIG.pdf_dir / '068057engo.pdf', 'Meteors tiny wanderers through space', 28),
    ],
)
def test_title_position(filename, title, page_number):
    extractor: JavaExtractor = JavaExtractor()
    issue: ExtractedPages = extractor.extract_pages(filename)

    page_text = ' '.join(str(issue.get_page(page_number).content).lower().split())
    expected_title_position = page_text.index(
        title.lower()
    )  # FIXME: Add expected_title_position to parameters instead of calculating it

    extracted_title_position, _ = get_best_candidate(
        title, [(position, title) for title, position in issue.get_page(page_number).titles]
    )

    assert extracted_title_position is not None
    assert expected_title_position - 10 < extracted_title_position <= expected_title_position
    assert expected_title_position == extracted_title_position


@pytest.mark.parametrize(
    'input_pdf, first_page, last_page, expected',
    [
        ('2_pages_1_empty.pdf', 1, None, 2),
        ('3_pages.pdf', 2, 100, 2),
        ('3_pages.pdf', 100, None, 0),
    ],
)
def test_pdf_to_txt_returns_correct_number_of_pages(input_pdf, first_page, last_page, expected):
    with TemporaryDirectory() as output_dir:
        file: Path = Path(CONFIG.test_files_dir / 'pdf' / input_pdf)
        extractor: ITextExtractor = JavaExtractor()
        extractor.pdf_to_txt(file, output_dir, first_page=first_page, last_page=last_page)
        result = len(list(Path(output_dir).iterdir()))
        assert result == expected
        assert not (Path(output_dir) / 'extract.log').exists()


@pytest.mark.java
def test_batch_extract_generates_expected_output():
    """Tests if batch_extract generates expected output. Output should be identical pdfbox_extractor's."""
    with TemporaryDirectory() as output_dir:
        files: List[Path] = get_filenames(CONFIG.test_files_dir / 'test.pdf')
        extractor: ITextExtractor = JavaExtractor()
        extractor.batch_extract(files, output_dir, first_page=1, last_page=None)

        assert len(sorted(Path(output_dir).glob('*.txt'))) == 8
        assert (Path(output_dir) / 'extract.log').exists()
        assert not filecmp.dircmp(output_dir, CONFIG.test_files_dir / 'expected/pdfbox').diff_files
        assert len(filecmp.dircmp(output_dir, CONFIG.test_files_dir / 'not_expected').diff_files) == 1
