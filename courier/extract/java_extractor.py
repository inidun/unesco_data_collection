# pyright: reportMissingImports=false
# pylint: disable=import-error, wrong-import-position, import-outside-toplevel, consider-using-from-import

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Union

import jpype
import jpype.imports
from appdirs import AppDirs
from pkg_resources import parse_version

from courier.config import get_config

CONFIG = get_config()

pdfcourier2text_path = CONFIG.project_root / 'courier/lib/pdfextract-1.0-SNAPSHOT.jar'


def get_pdfbox_path() -> Path:
    app_dir = AppDirs('python-pdfbox')
    cache_dir = Path(app_dir.user_cache_dir)
    file_list = list(cache_dir.glob('pdfbox-app-*.jar'))
    if not file_list:
        raise RuntimeError('PDFBox not found')
    return sorted(file_list, key=lambda x: parse_version(str(x)))[-1]


@dataclass
class ExtractedPage:
    pdf_page_number: int
    content: str
    titles: List[Tuple[str, int]]


@dataclass
class ExtractedIssue:
    """Container for extracted raw text, and titles (text and positiopn) for a single issue.

    Note:
      - Page numbers are not corrected for double-pages (represented as a single image in PDF).
    """

    pages: List[ExtractedPage]

    def __len__(self) -> int:
        return len(self.pages or [])

    def __str__(self) -> str:
        return '\n\n'.join([str(p.content) for p in self.pages])


# TODO: Add java args as option to JavaExtractor class
class JavaExtractor:
    def __init__(
        self,
        title_font_size: float = 5.5,
        min_title_length: int = 8,
    ):

        self.title_font_size = title_font_size
        self.min_title_length = min_title_length

        if str(pdfcourier2text_path) not in jpype.getClassPath():
            jpype.addClassPath(pdfcourier2text_path)

        if not jpype.isJVMStarted():
            jpype.addClassPath(get_pdfbox_path())
            jpype.startJVM(
                '-Dorg.apache.commons.logging.Log=org.apache.commons.logging.impl.NoOpLog', convertStrings=False
            )

        import se.umu.humlab.pdfextract as pdfextract  # isort: skip  # noqa: E402

        self.extractor = pdfextract.PDFCourier2Text(self.title_font_size, self.min_title_length)

    # FIXME: #48 Title position offset error
    def extract_issue(self, filename: Union[str, os.PathLike]) -> ExtractedIssue:
        filename = str(filename)
        pages = []
        for pdf_page_number, content in enumerate(self.extractor.extractText(filename), start=1):
            titles = [
                [(str(y.title), int(y.position)) for y in x] for x in self.extractor.getTitles()
            ]  # pylint: disable=W0631
            page: ExtractedPage = ExtractedPage(
                pdf_page_number=pdf_page_number,
                content=content,
                titles=titles[pdf_page_number - 1],
            )
            pages.append(page)

        issue: ExtractedIssue = ExtractedIssue(pages=pages)
        return issue
