import os
from os.path import basename, splitext

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


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
