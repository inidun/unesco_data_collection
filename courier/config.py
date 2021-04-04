import csv
import os
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from courier.courier_metadata import create_article_index


def get_project_root() -> Path:
    folder = os.getcwd()
    while os.path.split(folder)[1] not in ('', 'unesco_data_collection'):
        folder, _ = os.path.split(folder)
    return Path(folder)


@dataclass
class CourierConfig:  # pylint: disable=too-many-instance-attributes

    # Data paths
    base_data_dir: Path = (Path.home() / "data/courier").resolve()
    project_root: Path = get_project_root()

    pdf_dir: Path = base_data_dir / "pdf"
    pdfbox_txt_dir: Path = base_data_dir / "pdfbox/txt"
    pdfbox_xml_dir: Path = base_data_dir / "pdfbox/xml"
    tessseract_output_dir: Path = base_data_dir / "tesseract/txt"
    default_output_dir: Path = base_data_dir / "articles"
    test_files_dir: Path = base_data_dir / "test_files"
    test_output_dir: Path = project_root / "tests/output"

    # Metadata
    double_pages_file: Path = project_root / "data/courier/double_pages/double_pages.txt"
    exclusions_file: Path = project_root / "data/courier/double_pages/exclude.txt"
    overlapping_pages: Path = project_root / "data/courier/overlapping_pages.csv"
    courier_metadata: Path = project_root / "data/courier/UNESCO_Courier_metadata.csv"
    article_index: pd.DataFrame = create_article_index(courier_metadata)

    default_template: str = "article.xml.jinja"
    invalid_chars: re.Pattern = re.compile("[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]")

    # TODO: Move to courier metadata (Make metadate class)
    # FIXME: Don't use property
    @property
    def double_pages(self) -> dict:
        with open(self.exclusions_file, newline='') as fp:
            reader = csv.reader(fp, delimiter=';')
            exclusions = [x[0] for x in reader]
        with open(self.double_pages_file, "r") as fp:
            data = fp.readlines()
            filtered_data = [line for line in data if all(e not in line for e in exclusions)]
            pages = {os.path.basename(line)[:6]: list(map(int, line.split(" ")[1:])) for line in filtered_data}
        return pages
