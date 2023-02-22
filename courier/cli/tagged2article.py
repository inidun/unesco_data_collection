import os
from os.path import basename, splitext

import click
from loguru import logger

from courier.extract.utils import get_filenames
from courier.scripts.tagged_issue_to_articles import get_issue_articles, store_article_text


@click.command()
@click.option('--editorials/--no-editorials', default=False)
@click.option('--supplements/--no-supplements', default=False)
@click.option('--unindexed/--no-unindexed', default=False)
@click.argument('source', nargs=1)
@click.argument('target_folder', nargs=1)
def main(source: str, target_folder: str, editorials: bool, supplements: bool, unindexed: bool) -> None:
    os.makedirs(target_folder, exist_ok=True)

    logging_format: str = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}'
    logger.add(f'{target_folder}/info.log', format=logging_format, level='INFO')
    logger.add(f'{target_folder}/warnings.log', format=logging_format, level='WARNING')

    for filename in get_filenames(source, 'md'):
        _, year, courier_id = splitext(basename(filename))[0].split('_')
        articles = get_issue_articles(
            filename,
            extract_editorials=editorials,
            extract_supplements=supplements,
            extract_unindexed_articles=unindexed,
        )
        store_article_text(articles, target_folder, year, courier_id)
        logger.info(f'Extracted {basename(filename)}')


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
