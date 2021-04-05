import os
from pathlib import Path
from statistics import median
from typing import Dict, List, Union

import pdf2image

from courier.config import CourierConfig


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
    for file in Path(CourierConfig.pdf_dir).glob('*.pdf'):
        tot_pages.append(pdf2image.pdfinfo_from_path(file)["Pages"])
    return {
        "files": len(tot_pages),
        "pages": sum(tot_pages),
        "mean": round(sum(tot_pages) / len(tot_pages)),
        "median": round(median(tot_pages)),
    }
