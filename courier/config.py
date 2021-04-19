import csv
import os
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from loguru import logger

from courier.metadata import get_article_index_from_file

_config = None


def get_project_root() -> Path:
    folder = os.getcwd()
    while os.path.split(folder)[1] not in ('', 'unesco_data_collection'):
        folder, _ = os.path.split(folder)
    return Path(folder)


@dataclass
class CourierConfig:  # pylint: disable=too-many-instance-attributes

    # Base paths
    base_data_dir: Path = (Path.home() / 'data/courier').resolve()
    project_root: Path = get_project_root()

    # Folders
    metadata_dir: Path = base_data_dir / 'metadata'
    pdf_dir: Path = base_data_dir / 'pdf'
    pdfbox_txt_dir: Path = base_data_dir / 'pdfbox/txt'
    pdfbox_xml_dir: Path = base_data_dir / 'pdfbox/xml'
    tessseract_output_dir: Path = base_data_dir / 'tesseract/txt'
    article_output_dir: Path = base_data_dir / 'articles'
    test_files_dir: Path = base_data_dir / 'test_files'
    test_output_dir: Path = project_root / 'tests/output'

    # Metadata
    double_pages_file: Path = project_root / 'data/courier/double_pages/double_pages.csv'
    exclusions_file: Path = project_root / 'data/courier/double_pages/exclude_double_pages.csv'
    overlapping_pages: Path = project_root / 'data/courier/overlapping_pages.csv'
    courier_metadata: Path = project_root / 'data/courier/UNESCO_Courier_metadata.csv'
    article_index: pd.DataFrame = get_article_index_from_file(courier_metadata)

    default_template: str = 'article.xml.jinja'
    invalid_chars: re.Pattern = re.compile('[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')

    @property
    def double_pages(self) -> dict:
        with open(self.exclusions_file, newline='') as fp:
            reader = csv.reader(fp, delimiter=';')
            exclusions = [line[0] for line in reader]
        with open(self.double_pages_file, 'r') as fp:
            reader = csv.reader(fp, delimiter=';')
            filtered_data = [line for line in reader if all(e not in line for e in exclusions)]
            pages = {line[0]: list(map(int, line[1].split())) for line in filtered_data}
        return pages


def get_config() -> CourierConfig:
    global _config
    if _config is not None:
        pass  # logger.debug('Config already loaded.')
    if _config is None:
        logger.debug('Loading config.')
        _config = CourierConfig()
    return _config
