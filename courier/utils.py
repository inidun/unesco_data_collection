import csv
import functools
import operator
import os
from pathlib import Path
from statistics import median
from typing import Any, Dict, Iterable, List, Union

import pdf2image

from courier.config import get_config

CONFIG = get_config()


def flatten(list_of_list: Iterable[Iterable[Any]]) -> List[Any]:
    return functools.reduce(operator.iconcat, list_of_list, [])


def get_filenames(files: Union[str, os.PathLike]) -> List[Path]:
    items = []
    path = Path(files)
    if path.is_dir():
        items = list(path.glob("*.pdf"))
    elif path.is_file() and path.suffix == ".pdf":
        items.append(path)
    return items


def get_stats() -> Dict[str, int]:
    tot_pages = []
    for file in Path(CONFIG.pdf_dir).glob('*.pdf'):
        tot_pages.append(pdf2image.pdfinfo_from_path(file)["Pages"])
    return {
        "files": len(tot_pages),
        "pages": sum(tot_pages),
        "mean": round(sum(tot_pages) / len(tot_pages)),
        "median": round(median(tot_pages)),
    }


def get_double_pages(courier_id: str) -> list:

    with open(CONFIG.exclusions_file, newline='') as fp:
        reader = csv.reader(fp, delimiter=';')
        exclusions = [line[0] for line in reader]
    if courier_id in exclusions:
        return []

    with open(CONFIG.double_pages_file, "r") as fp:
        reader = csv.reader(fp, delimiter=';')
        pages = [list(map(int, line[1].split())) for line in reader if courier_id in line]

    return flatten(pages)
