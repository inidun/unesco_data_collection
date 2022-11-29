import os
import re
from pathlib import Path
from typing import Callable, List, Union

import argh
import pandas as pd
from loguru import logger
from thefuzz import process

from courier.config import get_config
from courier.elements import CourierIssue
from courier.overlap_check import get_overlapping_pages

CONFIG = get_config()


def create_regexp(title_string: str) -> str:
    tokens = re.findall('[a-zåäö]+', title_string.lower())
    expression = '[^a-zåäö]+'.join(tokens)
    return expression[1:]


def countinue_count(text: str) -> int:
    expr = r"\(continued|\(cont'd"
    m = re.findall(expr, text.lower(), re.IGNORECASE)
    return len(m)


def match_regex(text: str, title: str) -> bool:
    expr = create_regexp(title)
    m = re.search(expr, text, re.IGNORECASE)
    return bool(m)


def match_fuzzywuzzy(text: str, title: str, min_score: int = 90) -> bool:
    if not 0 <= min_score <= 100:
        raise ValueError('min_score must be in the range [0, 100]')
    lines = text.splitlines()
    value = process.extractOne(title, lines)
    return bool(value and value[1] > min_score)


def find_uppercase_sequences(text: str, min_word_len: int = 1, min_seq_len: int = 1) -> List[str]:
    expr = rf'\b[A-Z]{{{min_word_len},}}(?:\s+[A-Z]{{{min_word_len},}}){{{min_seq_len - 1},}}\b'
    return re.findall(expr, text)


def uppercase_sequence_count(text: str, min_word_len: int = 1, min_seq_len: int = 1) -> int:
    return len(find_uppercase_sequences(text, min_word_len, min_seq_len))


def corrected_page_number(courier_id: str, page_number: int) -> int:
    return page_number - len([dpn for dpn in CONFIG.double_pages.get(courier_id, []) if dpn < page_number])


def get_stats(
    article_index: pd.DataFrame, overlap: pd.DataFrame, match_function: Callable[[str, str], bool] = match_regex
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
        page_stat['uppercase_count'] = uppercase_sequence_count(text, 2, 2)

        for article_info in articles_on_page:
            title = article_info['catalogue_title']
            m = match_function(text, title)
            if m:
                page_stat['found'] += 1
            else:
                page_stat['not_found'] += 1

        found.append(page_stat)

    stats = pd.DataFrame(found)
    stats = stats[
        ['courier_id', 'page', 'page_corr', 'count', 'found', 'not_found', 'continued_count', 'uppercase_count']
    ]

    return stats


def get_match_function(func_name: str) -> Callable[[str, str], bool]:
    if func_name == 'regex':
        return match_regex
    if func_name == 'fuzzywuzzy':
        return match_fuzzywuzzy
    raise ValueError(func_name)


def save_stats(
    article_index: pd.DataFrame,
    output_folder: Union[str, os.PathLike],
    match_function: Union[Callable[[str, str], bool], str],
    sep: str = '\t',
    save_index: bool = False,
) -> None:

    if isinstance(match_function, str):
        match_function = get_match_function(match_function)

    Path(output_folder).mkdir(exist_ok=True, parents=True)

    stats = get_stats(
        article_index=article_index,
        overlap=get_overlapping_pages(article_index),
        match_function=match_function,
    )

    stats.to_csv(
        Path(output_folder) / f'overlap_stats_{match_function.__name__.replace("match_", "")}.csv',
        sep=sep,
        index=save_index,
    )


@argh.arg('--match-function', choices=['regex', 'fuzzywuzzy'])  # type: ignore
def main(
    output_folder: str = str(CONFIG.metadata_dir),  # noqa: B008
    match_function: str = 'regex',
) -> None:
    save_stats(CONFIG.article_index, output_folder, match_function)


if __name__ == '__main__':
    argh.dispatch_command(main)
