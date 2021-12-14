import csv
import os
from typing import List, Optional, Sequence, Union

import argh
import pandas as pd


def excel_to_csv(
    excel_file: Union[str, os.PathLike],
    csv_file: Union[str, os.PathLike],
    sheet_name: Optional[Union[str, int, List[Union[int, str]]]] = 0,
    index_col: Optional[Union[int, Sequence[int]]] = 0,
    sep: str = ';',
    quoting: Optional[int] = csv.QUOTE_NONNUMERIC,
    sort_index: bool = False,
) -> None:
    df = pd.read_excel(excel_file, sheet_name=sheet_name, index_col=index_col)
    if sort_index:
        df.sort_index(inplace=True)
    df.to_csv(csv_file, encoding='utf-8', sep=sep, quoting=quoting)


if __name__ == '__main__':
    argh.dispatch_command(excel_to_csv)
