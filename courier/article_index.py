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


def get_expanded_article_pages(page_ref: Optional[str]) -> List[int]:
    """['p. D-D', 'p. D', 'p. D, D ', 'p. D, D-D ', 'p.D-D', 'p.D',
    'p. D-D, D ', 'page D', 'p., D-D', 'p. D-D, D-D ']"""

    if page_ref is None:
        return []
    pr = re.sub(r'^(p\.\,?|pages?)', '', str(page_ref or '')).replace(' ', '').split(',')
    ix = itertools.chain(
        *(
            [list(range(int(x), int(y) + 1)) for x, y in [w.split('-') for w in pr if '-' in w]]
            + [[int(x)] for x in pr if '-' not in x]
        )
    )
    return sorted(list(ix))


def extract_page_ref(item: str) -> Optional[str]:
    pattern = r'(?:(?:p\.\,?|pages?)(?:\s*\d+(?:-\d+)*))(?:(?:(?:\,\s+)(?:\d{1,3}))(?:-\d{1,3})?)*'
    m = re.search(pattern, item)
    if m is None:
        logger.debug(f'No match found for "{item}"')
        return None
    return m.group(0)


def get_article_index_from_file(filename: Union[str, bytes, os.PathLike]) -> pd.DataFrame:
    """Returns a pandas data frame that contains a processed version of the Courier article index

    Args:
        filename (Union[str, bytes, os.PathLike]): [description]

    Returns:
        pd.DataFrame: [description]
    """

    columns = [
        'Record number',
        'Catalogue - Title',
        'Languages',
        'Document type',
        'Host item',
        'Catalogue - Publication date',
    ]
    dtypes = {'Record number': 'uint32', 'Document type': 'category'}

    article_index = pd.read_csv(filename, usecols=columns, sep=';', dtype=dtypes, memory_map=True)
    article_index.columns = [
        'record_number',
        'catalogue_title',
        'languages',
        'document_type',
        'host_item',
        'publication_date',
    ]

    article_index = article_index[article_index['document_type'] == 'article']
    article_index = article_index[article_index.languages.str.contains('eng')]
    article_index.reset_index()

    article_index['eng_host_item'] = article_index['host_item'].apply(get_english_host_item)
    article_index.drop(columns=['document_type', 'languages', 'host_item'], axis=1, inplace=True)

    article_index['page_ref'] = article_index['eng_host_item'].apply(extract_page_ref)
    article_index.loc[article_index.record_number == 187812, 'page_ref'] = 'p. 18-31'  # Manual fix
    article_index.loc[article_index.record_number == 64927, 'page_ref'] = 'p. 28-29'  # Manual fix

    article_index['pages'] = article_index.page_ref.apply(get_expanded_article_pages)
    article_index.drop(columns=['page_ref'], axis=1, inplace=True)

    article_index['courier_id'] = article_index.eng_host_item.apply(get_courier_id)

    article_index['year'] = article_index.publication_date.apply(lambda x: int(x[:4])).astype('uint16')

    # FIXME: Change index to record_number
    article_index = article_index.set_index(article_index['courier_id'].astype('uint32'))
    article_index.index.rename('id', inplace=True)

    return article_index[['courier_id', 'year', 'record_number', 'pages', 'catalogue_title']]


def article_index_to_csv(
    article_index: pd.DataFrame, output_folder: Union[str, os.PathLike], sep: str = '\t', save_index: bool = False
) -> None:
    Path(output_folder).mkdir(exist_ok=True)
    article_index.to_csv(Path(output_folder) / 'article_index.csv', sep=sep, index=save_index)


def get_issue_index_from_file(filename: Union[str, bytes, os.PathLike]) -> pd.DataFrame:
    """Returns a pandas data frame that contains a processed version of the Courier issue index

    Args:
        filename (Union[str, bytes, os.PathLike]): [description]

    Returns:
        pd.DataFrame: [description]
    """

    columns = [
        'Record number',
        'Catalogue - Title',
        'Languages',
        'Catalogue - Subjects',
        'Document type',
        'Catalogue - Publication date',
    ]
    dtypes = {'Record number': 'uint32', 'Document type': 'category'}

    issue_index = pd.read_csv(filename, usecols=columns, sep=';', dtype=dtypes, memory_map=True)
    issue_index.columns = [
        'courier_id',
        'title',
        'languages',
        'subjects',
        'document_type',
        'publication_date',
    ]

    issue_index = issue_index[issue_index['document_type'] == 'periodical issue']
    issue_index = issue_index[issue_index.languages.str.contains('eng')]
    issue_index.drop(columns=['document_type', 'languages'], axis=1, inplace=True)
    issue_index['year'] = issue_index.publication_date.apply(lambda x: int(x[:4])).astype('uint16')
    issue_index = issue_index.set_index(issue_index['courier_id'].astype('uint32'))
    issue_index.index.rename('id', inplace=True)
    issue_index.fillna(value={'subjects': ' '}, inplace=True)

    return issue_index


if __name__ == '__main__':
    pass
