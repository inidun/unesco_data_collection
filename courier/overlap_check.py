import csv
import os
from typing import Union

import pandas as pd

from courier.config import get_config

CONFIG = get_config()


def get_overlapping_pages(article_index: pd.DataFrame) -> pd.DataFrame:
    df_pages = article_index[['courier_id', 'record_number', 'pages']].explode('pages')
    df_pages['courier_id'] = df_pages.courier_id.astype('int')
    page_count = df_pages.groupby(['courier_id', 'pages']).size()
    page_count = page_count.reset_index()
    page_count.columns = ['courier_id', 'pages', 'count']
    overlapping_pages = page_count[page_count['count'] > 1]
    overlapping_pages = overlapping_pages.rename(columns={'pages': 'page'})
    overlapping_pages = overlapping_pages.reset_index(drop=True)
    return overlapping_pages


def save_overlapping_pages(
    overlap_df: pd.DataFrame, output_filename: Union[str, bytes, os.PathLike] = CONFIG.overlap_file
) -> None:
    overlap_df.to_csv(output_filename, sep='\t', index=False, quoting=csv.QUOTE_NONNUMERIC)


def create_copy_script(overlap_df: pd.DataFrame, copy_folder: str = './tmp') -> None:  # pragma: no cover
    overlap_df['#!/bin/bash'] = overlap_df.apply(
        lambda x: f'cp {int(x["courier_id"]):06}eng*_{x["page"]:04}.txt {copy_folder}', axis=1
    )
    d = overlap_df['#!/bin/bash']
    d.to_csv(CONFIG.project_root / 'courier/scripts/copy_overlapping_pages.sh', index=False, header='#!/bin/bash')


if __name__ == '__main__':
    pass
