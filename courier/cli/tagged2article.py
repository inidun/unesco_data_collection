import ast
import os
from os.path import basename, splitext
from pathlib import Path

import click
import pandas as pd
from loguru import logger

from courier.extract.utils import get_filenames
from courier.scripts.tagged_issue_to_articles import (
    get_issue_articles,
    load_article_index,
    store_article_text,
    verify_articles,
)


@click.command()
@click.option('--editorials/--no-editorials', default=False)
@click.option('--supplements/--no-supplements', default=False)
@click.option('--unindexed/--no-unindexed', default=False)
@click.argument('source', nargs=1)
@click.argument('target_folder', nargs=1)
@click.argument('article_index', required=False)
def main(
    source: str,
    target_folder: str,
    editorials: bool,
    supplements: bool,
    unindexed: bool,
    article_index: str | None = None,
) -> None:
    os.makedirs(target_folder, exist_ok=True)

    logging_format: str = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}'
    logger.add(f'{target_folder}/info.log', format=logging_format, level='INFO')
    logger.add(f'{target_folder}/warnings.log', format=logging_format, level='WARNING')

    if article_index:
        index: pd.DataFrame = load_article_index(article_index)
        index.to_csv(os.path.join(target_folder, 'document_index.csv'), sep='\t', encoding='utf-8')

    for filename in get_filenames(source, 'md'):
        _, year, courier_id = splitext(basename(filename))[0].split('_')
        articles = get_issue_articles(
            filename,
            extract_editorials=editorials,
            extract_supplements=supplements,
            extract_unindexed_articles=unindexed,
        )

        if article_index:
            logger.info(f'Verifying {basename(filename)}')
            verify_articles(articles, index)

        store_article_text(articles, target_folder, year, courier_id)
        logger.info(f'Extracted {basename(filename)}')

    if article_index:
        verify_extracted(target_folder, index)


def verify_extracted(target_folder: str | os.PathLike, index: pd.DataFrame) -> None:
    year_mismatch = index[~index.duplicated(subset=['courier_id', 'year'], keep=False)]['record_number'].to_list()
    if year_mismatch:
        logger.error(f'Articles with mismatching years: {", ".join(map(str, year_mismatch))}')

    duplicated_record_numbers = set(
        index[index.duplicated(subset=['record_number'], keep=False)]['record_number'].to_list()
    )
    if duplicated_record_numbers:
        logger.error(f'Index error. Duplicated record_numbers: {", ".join(map(str, duplicated_record_numbers))}')

    n_extracted = len([x for x in Path(target_folder).iterdir() if x.suffix == '.txt'])
    n_expected = index.shape[0]
    missing = n_expected - n_extracted - len(duplicated_record_numbers)
    if missing:
        logger.error(f'Missing {missing} articles. Extracted {n_extracted}. Expected {index.shape[0]}')

    articles_with_no_pages = index[index.pages.apply(lambda x: len(ast.literal_eval(x))) == 0].record_number.to_list()
    if articles_with_no_pages:
        logger.error(f'Missing (no pages in index): {", ".join(str(x) for x in articles_with_no_pages)}')

    missing_articles = []
    for _, row in index.iterrows():
        if not os.path.isfile(os.path.join(target_folder, row['filename'])):
            missing_articles.append(row['record_number'])

    not_extracted = [x for x in missing_articles if x not in year_mismatch and x not in articles_with_no_pages]

    if not_extracted:
        logger.error(f'Missing (unknown reason): {", ".join(map(str, not_extracted))}')


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
