import csv
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd

from courier.article_index import get_article_index_from_file, get_issue_index_from_file

# from loguru import logger


_config = None


def get_project_root() -> Path:
    folder = os.getcwd()
    while os.path.split(folder)[1] not in ('', 'unesco_data_collection'):
        folder, _ = os.path.split(folder)
    return Path(folder)


def read_double_pages(
    exclusions_file: Union[str, os.PathLike], double_pages_file: Union[str, os.PathLike]
) -> Dict[str, List[int]]:
    with open(exclusions_file, newline='', encoding='utf-8') as fp:
        reader = csv.reader(fp, delimiter=';')
        exclusions = [line[0] for line in reader]
    with open(double_pages_file, 'r', encoding='utf-8') as fp:
        reader = csv.reader(fp, delimiter=';')
        filtered_data = [line for line in reader if all(e not in line for e in exclusions)]
        pages = {line[0]: list(map(int, line[1].split())) for line in filtered_data}
    return pages


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
    test_files_dir: Path = project_root / 'tests/fixtures/courier'

    # Metadata
    metadata_dir: Path = project_root / 'data/courier/metadata'
    metadata_file: Path = metadata_dir / 'UNESCO_Courier_metadata.csv'
    double_pages_file: Path = metadata_dir / 'double_pages.csv'
    exclusions_file: Path = metadata_dir / 'double_pages_exclusions.csv'
    overlap_file: Path = metadata_dir / 'overlap.csv'
    correction_file: Path = metadata_dir / 'article_index_page_corrections.csv'

    issue_index: pd.DataFrame = None
    double_pages: Dict[str, List[int]] = field(default_factory=dict)
    _article_index: pd.DataFrame = field(init=False, default=None)

    def __post_init__(self) -> None:
        self.issue_index: pd.DataFrame = get_issue_index_from_file(self.metadata_file)
        self.double_pages: Dict[str, List[int]] = read_double_pages(self.exclusions_file, self.double_pages_file)

    @property
    def article_index(self) -> pd.DataFrame:
        if self._article_index is None:
            self._article_index: pd.DataFrame = get_article_index_from_file(self.metadata_file, self.correction_file)
        return self._article_index

    def get_issue_article_index(self, courier_id: str) -> List[Dict[str, Any]]:
        index: pd.DataFrame = self.article_index[self.article_index['courier_id'] == courier_id]
        article_index: List[Dict[str, Any]] = [record for record in index.to_dict('records')]
        return article_index

    def get_courier_ids(self) -> List[str]:
        issues = sorted(list(Path(self.pdf_dir).glob('*.pdf')))
        return [x.stem for x in issues]

    def get_issue_filename(self, courier_id: str) -> str:
        return str(list(self.pdf_dir.glob(f'{courier_id}*.pdf'))[0])


def get_config() -> CourierConfig:
    global _config
    if _config is not None:
        pass  # logger.debug('Config already loaded.')
    if _config is None:
        # logger.debug('Loading config.')
        _config = CourierConfig()
    return _config
