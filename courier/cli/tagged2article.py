from os.path import basename, splitext

import click
from loguru import logger

from courier.extract.utils import get_filenames
from courier.scripts.tagged_issue_to_articles import get_issue_articles, store_article_text


@click.command()
@click.argument('source', nargs=1)
@click.argument('target_folder', nargs=1)
def main(source: str, target_folder: str) -> None:

    for filename in get_filenames(source, 'md'):
        _, year, courier_id = splitext(basename(filename))[0].split('_')
        articles = get_issue_articles(filename)
        store_article_text(articles, target_folder, year, courier_id)
        logger.info(f'Extracted {basename(filename)}')


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
