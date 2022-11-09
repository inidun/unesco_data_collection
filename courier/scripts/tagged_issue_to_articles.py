from __future__ import annotations

import os
import re
from collections import defaultdict
from os.path import basename
from os.path import join as jj
from os.path import splitext

import click
from loguru import logger


def get_issue_articles(filename: str | os.PathLike) -> dict[str, tuple]:

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

        unknown_article_match: re.Match[str] | None = re.match(r'^#{1,3}\s+UNINDEXED_ARTICLE', segment)
        if unknown_article_match is not None:
            article_id = f'@{courier_id}-{str(page_number)}'
            article_text: str = ''.join(segment.split(sep='\n', maxsplit=2)[1:])
            article_bag[article_id] = [(article_id, page_number, article_text, f'Unknown article {article_id}')]
            logger.info(f'Extracted unindexed article - {article_id}')
            continue

        article_match: re.Match[str] | None = re.match(r'^#{1,3}\s*(\d+):\s*(.*)\n', segment)
        if article_match is not None:
            article_id = str(article_match.groups()[0])
            article_title: str = str(article_match.groups()[1])
            article_text = ''.join(segment.split(sep='\n', maxsplit=2)[1:])
            article_bag[article_id].append((article_id, page_number, article_text, article_title))
            logger.info(f'Extracted article segment {article_id}:{page_number} - {article_title}')
            continue

    articles: dict = {
        article_id: (article_id, [x[1] for x in data], '\n'.join([x[2] for x in data]))
        for article_id, data in article_bag.items()
    }
    return articles


def store_article_text(articles: dict, folder: str, year: str, courier_id: str) -> None:

    os.makedirs(folder, exist_ok=True)

    for article_id, (_, _, article_text) in articles.items():
        filename: str = jj(folder, f'{year}_{courier_id}_{article_id}.txt')
        with open(filename, encoding='utf-8', mode='w') as fp:
            fp.write(article_text)


@click.command()
@click.argument('filename')
@click.argument('target_folder')
def main(filename: str, target_folder: str) -> None:

    _, year, courier_id = splitext(basename(filename))[0].split('_')
    articles = get_issue_articles(filename)
    store_article_text(articles, target_folder, year, courier_id)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
