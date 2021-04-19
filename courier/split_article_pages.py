import os
import re
from pathlib import Path
from typing import Union

import pandas as pd
from loguru import logger

from courier.config import get_config
from courier.elements import CourierIssue
from courier.overlap_check import get_overlapping_pages
from courier.utils import corrected_page_number

CONFIG = get_config()


def create_regexp(title_string: str) -> str:
    tokens = re.findall('[a-zåäö]+', title_string.lower())
    expression = '[^a-zåäö]+'.join(tokens)
    return expression[1:]


def get_stats(article_index: pd.DataFrame, overlap: pd.DataFrame) -> pd.DataFrame:

    index = article_index[['courier_id', 'catalogue_title', 'pages']]
    overlap['courier_id'] = overlap.courier_id.apply(lambda x: str(x).zfill(6))
    found = []

    for row in overlap.to_dict('records'):

        articles_on_page = index[
            (index.courier_id == row['courier_id']) & index.pages.apply(lambda x, r=row: r['page'] in x)
        ]
        articles_on_page = articles_on_page.to_dict('records')

        if row['count'] != len(articles_on_page):
            logger.warning(f'Page count mismatch: {row["courier_id"]}')

        row_page = corrected_page_number(row['courier_id'], row['page'])
        text = CourierIssue(row['courier_id']).get_page(row_page).text

        page_stat = dict(row)
        page_stat['page_corr'] = row_page
        page_stat['found'] = 0
        page_stat['not_found'] = 0

        for article_info in articles_on_page:
            title = article_info['catalogue_title']
            expr = create_regexp(title)
            m = re.search(expr, text, re.IGNORECASE)
            if m:
                page_stat['found'] += 1
            else:
                page_stat['not_found'] += 1

        found.append(page_stat)

    stats = pd.DataFrame(found)
    stats = stats[['courier_id', 'page', 'page_corr', 'count', 'found', 'not_found']]

    return stats


def save_stats(
    output_file: Union[str, os.PathLike] = CONFIG.metadata_dir / 'overlap_stats.csv',
    sep: str = '\t',
    save_index: bool = False,
) -> None:

    output_folder = Path(output_file).parent
    Path(output_folder).mkdir(exist_ok=True, parents=True)

    stats = get_stats(
        article_index=CONFIG.article_index,
        overlap=get_overlapping_pages(CONFIG.article_index),
    )
    stats.to_csv(Path(output_file), sep=sep, index=save_index)


if __name__ == '__main__':
    save_stats()
