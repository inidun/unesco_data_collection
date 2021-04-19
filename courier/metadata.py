import itertools
import os
import re
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
from loguru import logger


def get_english_host_item(host_item: str) -> Optional[str]:
    items = [x for x in host_item.split('|') if x.endswith('eng')]
    if len(items) == 0:
        return None
    if len(items) > 1:
        raise ValueError(f'Ambiguity: Input has duplicate titles. {items}')
    return items[0]


def get_courier_id(eng_host_item: str) -> Optional[str]:
    m = re.match(r'.*\s(\d+)(\seng$)', eng_host_item)
    if not m:
        logger.debug(f'No match found for "{eng_host_item}"')
        return None
    courier_id = m.group(1)
    if len(courier_id) > 6:
        raise ValueError(f'ID too long: {courier_id}. Must be <= 6')
    return courier_id.zfill(6)


def get_expanded_article_pages(page_ref: str) -> List[int]:
    """['p. D-D', 'p. D', 'p. D, D ', 'p. D, D-D ', 'p.D-D', 'p.D',
    'p. D-D, D ', 'page D', 'p., D-D', 'p. D-D, D-D ']"""

    page_ref = re.sub(r'^(p\.\,?|pages?)', '', page_ref).replace(' ', '').split(',')
    ix = itertools.chain(
        *(
            [list(range(int(x), int(y) + 1)) for x, y in [w.split('-') for w in page_ref if '-' in w]]
            + [[int(x)] for x in page_ref if '-' not in x]
        )
    )
    return sorted(list(ix))


def get_article_index_from_file(filename: Union[str, bytes, os.PathLike]) -> pd.DataFrame:

    # FIXME: Use usecols
    df = pd.read_csv(filename, sep=';')  # 8313

    df.columns = [
        'record_number',
        'catalogue_title',
        'authors',
        'titles_in_other_languages',
        'languages',
        'series',
        'catalogue_subjects',
        'document_type',
        'host_item',
        'publication_date',
        'notes',
    ]

    df = df[df['document_type'] == 'article']  # 7639
    df = df[df.languages.str.contains('eng')]  # 7612

    df['eng_host_item'] = df['host_item'].apply(get_english_host_item)
    df = df.copy()

    df['page_ref'] = df['eng_host_item'].str.extract(
        r'((?:p\.\,?|pages?)(?:\s*\d+(?:-\d+)*)(?:\,\s*\d{1,3}(?:-\d{1,3})*\s)*)'
    )[0]

    df.loc[df.record_number == 187812, 'page_ref'] = 'p. 18-31'
    df.loc[df.record_number == 64927, 'page_ref'] = 'p. 28-29'

    df['courier_id'] = df.eng_host_item.apply(get_courier_id)
    df['pages'] = df.page_ref.apply(get_expanded_article_pages)
    df['year'] = df.publication_date.apply(lambda x: int(x[:4]))

    df['notes'] = df.notes.fillna('').str.replace('\n', ' ')

    return df[
        [
            'record_number',
            'catalogue_title',
            'eng_host_item',
            'courier_id',
            'year',
            'publication_date',
            'pages',
            'notes',
        ]
    ]


def article_index_to_csv(
    article_index: pd.DataFrame,
    output_folder: Union[str, os.PathLike],
    sep: str = '\t',
    save_index: bool = False,
) -> None:
    Path(output_folder).mkdir(exist_ok=True)
    article_index.to_csv(Path(output_folder) / 'article_index.csv', sep=sep, index=save_index)
