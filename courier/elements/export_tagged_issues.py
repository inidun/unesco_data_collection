# pylint: disable=redefined-outer-name
import os
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
from typing import List, Union

from loguru import logger

from courier.article_index import article_index_to_csv
from courier.config import get_config
from courier.elements.assign_page_service import AssignPageService
from courier.elements.consolidate_text_service import ConsolidateTextService, get_best_candidate
from courier.elements.elements import Article, CourierIssue
from courier.utils import flatten, split_by_idx

CONFIG = get_config()
# CONFIG.pdf_dir = CONFIG.base_data_dir / 'pdf_reocr/all'
# CONFIG.articles_dir = CONFIG.base_data_dir / 'pdf_reocr/all_out'


def export_tagged_issue(
    courier_id: str,
    export_folder: Union[str, os.PathLike] = CONFIG.articles_dir / 'exported',
) -> None:
    issue: CourierIssue = CourierIssue(courier_id)
    issue_article_index = CONFIG.get_issue_article_index(courier_id)
    year = issue_article_index[0]['year']
    AssignPageService().assign(issue)
    ConsolidateTextService().consolidate(issue)

    url = f'{os.environ.get("pdf_url_base")}{os.path.basename(CONFIG.get_issue_filename(courier_id))}'
    non_article_heading = '### IGNORE'

    texts: List[str] = []
    num_issue_errors = 0

    for page in issue.pages:

        num_issue_errors += len(page.errors)
        texts.append(f'## [Page {page.page_number}]({url}#page={page.page_number}) {str(len(page.errors))}')

        if len(page.articles) == 0:
            texts.append(non_article_heading)
            texts.append(page.text)
        else:

            sorted_positioned_articles: list[tuple[int, Article]] = sorted(
                [(get_best_candidate(a.catalogue_title, page.titles)[0] or 0, a) for a in page.articles],
                key=lambda x: x[0],
            )

            positions, articles = zip(*sorted_positioned_articles)

            if min(positions) > 0:
                texts.append(non_article_heading)

            title_headings = [f'### {article.record_number}: {article.catalogue_title}' for article in articles]

            texts += flatten(zip_longest(split_by_idx(page.text, positions), title_headings, fillvalue=None))

    Path(export_folder).mkdir(parents=True, exist_ok=True)
    filename: Path = Path(export_folder) / f'tagged_{year}_{courier_id}.md'

    with open(filename, 'w', encoding='utf-8') as fp:
        fp.write(f'# [{courier_id}]({url}) {str(num_issue_errors)}\n\n')
        fp.write('\n\n'.join(filter(None, texts)))


def main() -> None:
    export_folder: Path = CONFIG.articles_dir / f'tagged_issues_{datetime.now().strftime("%Y-%m-%dT%H%M")}'
    article_index_to_csv(CONFIG.article_index, export_folder)
    logger.info('courier_id;year;record_number;assigned;not_found;total')

    courier_ids = [x[:6] for x in CONFIG.get_courier_ids()]

    for courier_id in courier_ids:
        try:
            export_tagged_issue(courier_id, export_folder)
        except ValueError as e:
            logger.info(e)


if __name__ == '__main__':

    main()
