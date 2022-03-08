# pylint: disable=redefined-outer-name
import os
from datetime import datetime
from html import escape
from pathlib import Path
from typing import List, Union

from loguru import logger

from courier.config import get_config
from courier.elements.assign_page_service import AssignPageService
from courier.elements.consolidate_text_service import get_best_candidate
from courier.elements.elements import CourierIssue

CONFIG = get_config()


def export_tagged_issue(
    courier_id: str,
    export_folder: Union[str, os.PathLike] = CONFIG.articles_dir / 'exported',
) -> None:

    issue: CourierIssue = CourierIssue(courier_id)
    issue_article_index = CONFIG.get_issue_article_index(courier_id)
    year = issue_article_index[0]['year']
    AssignPageService().assign(issue)

    texts: List[str] = []
    texts.append('<?xml version="1.0" encoding="UTF-8"?>')
    texts.append(f'<document id="{courier_id}">')

    for page in issue.pages:
        texts.append(f'<page i="{page.page_number}">')

        if len(page.articles) == 0:
            texts.append(escape(page.text, quote=False))

        elif len(page.articles) == 1:
            article = page.articles[0]
            pos, _ = get_best_candidate(article.catalogue_title, page.titles)

            if pos is None:
                texts.append(
                    f'<article record_number="{article.record_number}" title="{article.catalogue_title}" i="{page.page_number}">'
                )
                texts.append(escape(page.text, quote=False))

            else:
                texts.append(escape(page.text[:pos], quote=False))
                texts.append(
                    f'<article record_number="{article.record_number}" title="{article.catalogue_title}" i="{page.page_number}">'
                )
                texts.append(escape(page.text[pos:], quote=False))

            texts.append('</article>')

        else:

            for article in page.articles:

                texts.append(
                    f'<article record_number="{article.record_number}" title="{article.catalogue_title}" i="{page.page_number}">'
                )
            texts.append(escape(page.text, quote=False))

        texts.append('</page>')
    texts.append('</document>')

    Path(export_folder).mkdir(parents=True, exist_ok=True)
    filename: Path = Path(export_folder) / f'tagged_{year}_{courier_id}.xml'

    with open(filename, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(texts))


def main() -> None:
    export_folder: Path = CONFIG.articles_dir / f'tagged_issues_{datetime.now().strftime("%Y-%m-%dT%H%M")}'
    logger.info('courier_id;year;record_number;assigned;not_found;total')

    courier_ids = [x[:6] for x in CONFIG.get_courier_ids()]

    for courier_id in courier_ids:
        try:
            export_tagged_issue(courier_id, export_folder)
        except ValueError as e:
            logger.info(e)


if __name__ == '__main__':
    main()
