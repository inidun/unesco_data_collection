# pylint: disable=redefined-outer-name
import os
from datetime import datetime
from html import escape
from itertools import zip_longest
from pathlib import Path
from typing import List, Union

from loguru import logger

from courier.config import get_config
from courier.elements.assign_page_service import AssignPageService
from courier.elements.consolidate_text_service import get_best_candidate
from courier.elements.elements import CourierIssue
from courier.utils import flatten, split_by_idx

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
    texts.append(f'# {courier_id}')

    for page in issue.pages:
        texts.append(f'## Page {page.page_number}')
        if len(page.articles) == 0:
            texts.append('### Non-article text')
            texts.append(escape(page.text, quote=False))
        else:
            # fmt: off
            positions, titles = map(list, zip(*sorted([(get_best_candidate(a.catalogue_title, page.titles)[0] or 0, a.catalogue_title) for a in page.articles], key=lambda x: x[0])))
            # fmt: on

            if min(positions) > 0:  # type-ignore
                texts.append('### Non-article text')

            # FIXME: return article instead and add more info to titles
            titles = [f'### {title}' for title in titles]

            # FIXME: typing of positions
            texts += flatten(zip_longest(split_by_idx(escape(page.text, quote=False), positions), titles, fillvalue=None))  # type: ignore

    Path(export_folder).mkdir(parents=True, exist_ok=True)
    filename: Path = Path(export_folder) / f'tagged_{year}_{courier_id}.md'

    with open(filename, 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(filter(None, texts)))


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
