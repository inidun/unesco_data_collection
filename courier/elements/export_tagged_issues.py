# pylint: disable=redefined-outer-name
import os
from datetime import datetime
from pathlib import Path
from typing import List, Union

from loguru import logger

from courier.config import get_config
from courier.elements.assign_page_service import AssignPageService
from courier.elements.consolidate_text_service import ConsolidateTextService
from courier.elements.elements import CourierIssue

CONFIG = get_config()


def export_tagged_issue(
    courier_id: str,
    export_folder: Union[str, os.PathLike] = CONFIG.articles_dir / 'exported',
) -> None:
    issue: CourierIssue = CourierIssue(courier_id)

    issue_article_index = CONFIG.get_issue_article_index(courier_id)

    AssignPageService().assign(issue)
    ConsolidateTextService().consolidate(issue)
    Path(export_folder).mkdir(parents=True, exist_ok=True)
    year = issue_article_index[0]['year']

    texts: List[str] = []

    for page in issue.pages:
        texts.append(f'<page i="{page.page_number}">')
        if len(page.articles) == 0:
            texts.append(page.text)
        # TODO: Use position
        elif len(page.articles) == 1:
            texts.append(f'<article record_number="{page.articles[0].catalogue_title} " i="{page.page_number}">')
            texts.append(page.text)
            texts.append('</article>')

        texts.append('</page>')

    filename: Path = Path(export_folder) / f'tagged_{year}_{courier_id}.txt'

    with open(filename, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(texts))


def main() -> None:
    export_folder: Path = CONFIG.articles_dir / f'tagged_issues_{datetime.now().strftime("%Y-%m-%dT%H%M")}'

    logger.trace('courier_id;year;record_number;assigned;not_found;total')

    courier_ids = [x[:6] for x in CONFIG.get_courier_ids()]

    for courier_id in courier_ids:
        if courier_id not in CONFIG.article_index.courier_id.values:
            continue

        export_tagged_issue(courier_id, export_folder)


if __name__ == '__main__':
    main()
