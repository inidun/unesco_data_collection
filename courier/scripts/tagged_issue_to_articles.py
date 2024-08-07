from __future__ import annotations

import ast
import os
import re
from collections import defaultdict
from io import StringIO
from os.path import basename
from os.path import join as jj
from os.path import splitext

import click
import pandas as pd
from loguru import logger


def get_issue_articles(  # pylint: disable=too-many-statements
    filename: str | os.PathLike,
    extract_editorials: bool = False,
    extract_supplements: bool = False,
    extract_unindexed_articles: bool = False,
) -> dict[str, tuple]:
    """Extracts articles from a markdown encoded Courier issue file.

    Returns a dictionary where the key is the `article_id`. If the article is indexed, i.e. it has a `record_number`, the `article_id` is the same as the article's `record_number`, otherwise a new `article_id` is generated. The dictionary's value is a tuple containing the `article_id`, a list of pages where the article is found, and the complete text of the article.

    Args:
        filename (str | os.PathLike): Path to tagged Courier issue
        extract_editorials (bool, optional): Extract unindexed editorials. Defaults to False.
        extract_supplements (bool, optional): Extract unindexed supplements. Defaults to False.
        extract_unindexed_articles (bool, optional): Extract unindexed articles. Defaults to False.

    Returns:
        dict[str, tuple]: A dict with `article_id` as key and (`article_id`, list of pages, article text) as value
    """

    with open(filename, 'r', encoding='utf-8') as fp:
        issue_str: str = fp.read()

    courier_id: str = splitext(basename(filename))[0].split('_')[2]

    segments: list[str] = re.split('\n#', issue_str, maxsplit=0)

    page_number: int = 0
    article_bag: defaultdict[str, list[tuple[str, int, str, str]]] = defaultdict()
    article_bag.default_factory = list

    for segment in segments:
        page_match: re.Match[str] | None = re.match(r'^#\s*\[Page\s*(\d+)\]', segment)
        if page_match is not None:
            page_number = int(page_match.groups(0)[0])
            continue

        ignore_match: re.Match[str] | None = re.match(r'^#{1,3}\s+IGNORE', segment)
        if ignore_match is not None:
            continue

        unknown_supplement_match: re.Match[str] | None = re.match(r'^#{1,3}\s+UNINDEXED_SUPPLEMENT', segment)
        if unknown_supplement_match is not None:
            if not extract_supplements:
                logger.info(f'Skipped supplement {basename(filename)}:{page_number}')
                continue

            supplement_id: str = f's{courier_id}-{str(page_number)}'
            supplement_text: str = ''.join(segment.split(sep='\n', maxsplit=2)[1:])
            article_bag[supplement_id] = [
                (supplement_id, page_number, supplement_text, f'Unindexed supplement {supplement_id}')
            ]
            logger.debug(f'Extracted supplement - {supplement_id}')
            continue

        editorial_match: re.Match[str] | None = re.match(r'^#{1,3}\s+EDITORIAL', segment)
        if editorial_match is not None:
            if not extract_editorials:
                logger.info(f'Skipped editorial {basename(filename)}:{page_number}')
                continue

            editorial_id: str = f'e{courier_id}-{str(page_number)}'
            editorial_text: str = ''.join(segment.split(sep='\n', maxsplit=2)[1:])
            article_bag[editorial_id] = [(editorial_id, page_number, editorial_text, f'Editorial {editorial_id}')]
            logger.debug(f'Extracted editorial - {editorial_id}')
            continue

        unindexed_article_match: re.Match[str] | None = re.match(r'^#{1,3}\s+UNINDEXED_ARTICLE', segment)
        if unindexed_article_match is not None:
            logger.warning(f'Unindexed article {basename(filename)}:{page_number}')
            if not extract_unindexed_articles:
                continue

            unindexed_id = f'a{courier_id}-{str(page_number)}'
            unindexed_text: str = ''.join(segment.split(sep='\n', maxsplit=2)[1:])
            article_bag[unindexed_id] = [
                (unindexed_id, page_number, unindexed_text, f'Unindexed article {unindexed_id}')
            ]
            logger.debug(f'Extracted unindexed article - {unindexed_id}')
            continue

        article_match: re.Match[str] | None = re.match(r'^#{1,3}\s*(\d+):\s*(.*)\n', segment)
        if article_match is not None:
            article_id = str(article_match.groups()[0])
            article_title: str = str(article_match.groups()[1])
            article_text = ''.join(segment.split(sep='\n', maxsplit=2)[1:])
            article_bag[article_id].append((article_id, page_number, article_text, article_title))
            logger.debug(f'Extracted article segment {article_id}:{page_number} - {article_title}')
            continue

    articles: dict = {
        article_id: (article_id, [x[1] for x in data], '\n'.join([x[2] for x in data]))
        for article_id, data in article_bag.items()
    }
    return articles


def verify_articles(articles: dict, index: pd.DataFrame) -> None:
    """Verifies articles using article index

    Args:
        articles (dict): Dict with article data
        index (pd.DataFrame): Article index

    """
    for record_number, data in articles.items():
        record_number = int(record_number)
        if record_number not in index.record_number.values:
            logger.error(f'Record number not in article index: {record_number}')
            continue
        try:
            index_pages = ast.literal_eval(index[index.record_number == record_number]['pages'].values[0])
        except SyntaxError as e:
            logger.error(f'Invalid page numbers in index. Record number: {record_number}. {e.msg}: {e.text}')
            continue
        article_pages = list(dict.fromkeys(data[1]))
        if not all(page in index_pages for page in article_pages):
            logger.error(
                f'Page mismatch. Record number: {record_number}. Pages according to index: {index_pages}. Pages found in tagged file: {article_pages}.'
            )
            continue


def store_article_text(articles: dict, folder: str, year: str, courier_id: str) -> None:
    """Saves articles to folder. One file per article.

    Args:
        articles (dict): Dict containing article data
        folder (str): Output folder
        year (str): Puplication year
        courier_id (str): Courier ID
    """
    os.makedirs(folder, exist_ok=True)

    for article_id, (_, _, article_text) in articles.items():
        filename: str = jj(folder, f'{year}_{courier_id}_{article_id}.txt')
        with open(filename, encoding='utf-8', mode='w') as fp:
            fp.write(article_text)


def load_article_index(filename: str | os.PathLike | StringIO) -> pd.DataFrame:
    """Loads article index from disk and returns it as a DataFrame

    Args:
        filename (str | os.PathLike | StringIO): Path to article index

    Returns:
        pd.DataFrame: Article index
    """
    article_index = None

    if str(filename).endswith('.xlsx'):
        article_index = pd.read_excel(filename)
    if str(filename).endswith('.csv') or isinstance(filename, StringIO):
        article_index = pd.read_csv(filename, sep=';', encoding='utf-8')

    if article_index is not None:
        article_index.columns = ['courier_id', 'year', 'record_number', 'pages', 'catalogue_title', 'authors']
    article_index.sort_values(by=['year', 'courier_id', 'record_number'], inplace=True)
    article_index['filename'] = (
        article_index.year.astype(str)
        + '_'
        + article_index.courier_id.astype(str).str.zfill(6)
        + '_'
        + article_index.record_number.astype(str)
        + '.txt'
    )
    article_index.reset_index(drop=True, inplace=True)
    article_index['document_id'] = article_index.index
    article_index.set_index('document_id', drop=True, inplace=True)
    return article_index


@click.command()
@click.argument('filename')
@click.argument('target_folder')
@click.argument('article_index')
def main(filename: str, target_folder: str, article_index: str) -> None:
    _, year, courier_id = splitext(basename(filename))[0].split('_')
    articles = get_issue_articles(filename)
    article_index: pd.DataFrame = load_article_index(article_index)
    verify_articles(articles, article_index)
    store_article_text(articles, target_folder, year, courier_id)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
