import os
import re
from pathlib import Path
from typing import Callable, Union

import argh
import pandas as pd
from fuzzywuzzy import process
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


def countinue_count(text: str) -> int:
    expr = r"\(continued|\(cont'd"
    m = re.findall(expr, text.lower(), re.IGNORECASE)
    return len(m)


def find_title_by_regex(text: str, title: str) -> bool:
    expr = create_regexp(title)
    m = re.search(expr, text, re.IGNORECASE)
    return bool(m)


def find_title_by_fuzzymatch(text: str, title: str) -> bool:
    lines = text.splitlines()
    _, value = process.extractOne(title, lines)
    return bool(value > 90)


def get_stats(
    article_index: pd.DataFrame, overlap: pd.DataFrame, match_function: Callable[[str, str], bool] = find_title_by_regex
) -> pd.DataFrame:

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
        page_stat['continued_count'] = countinue_count(text)

        for article_info in articles_on_page:
            title = article_info['catalogue_title']
            m = match_function(text, title)
            if m:
                page_stat['found'] += 1
            else:
                page_stat['not_found'] += 1

        found.append(page_stat)

    stats = pd.DataFrame(found)
    stats = stats[['courier_id', 'page', 'page_corr', 'count', 'found', 'not_found', 'continued_count']]

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
        match_function=find_title_by_fuzzymatch,
    )
    stats.to_csv(Path(output_file), sep=sep, index=save_index)


if __name__ == '__main__':
    argh.dispatch_command(save_stats)
