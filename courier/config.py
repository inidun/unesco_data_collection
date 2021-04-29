import csv
import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from courier.article_index import get_article_index_from_file

# from loguru import logger


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
    pdf_dir: Path = base_data_dir / 'pdf'
    pages_dir: Path = base_data_dir / 'pages'
    xml_dir: Path = base_data_dir / 'xml'
    articles_dir: Path = base_data_dir / 'articles'
    test_files_dir: Path = base_data_dir / 'test_files'

    # Metadata
    metadata_dir: Path = project_root / 'data/courier/metadata'
    metadata_file: Path = metadata_dir / 'UNESCO_Courier_metadata.csv'
    double_pages_file: Path = metadata_dir / 'double_pages.csv'
    exclusions_file: Path = metadata_dir / 'double_pages_exclusions.csv'
    overlap_file: Path = metadata_dir / 'overlap.csv'
    article_index: pd.DataFrame = get_article_index_from_file(metadata_file)

    default_template: str = 'article.xml.jinja'

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
        # logger.debug('Loading config.')
        _config = CourierConfig()
    return _config
