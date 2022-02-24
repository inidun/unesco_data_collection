import glob
import os
from pathlib import Path
from typing import Union

import argh
import pandas as pd
from jinja2 import Environment, PackageLoader, select_autoescape
from loguru import logger
from tqdm import tqdm

from courier.article_index import article_index_to_csv
from courier.config import get_config
from courier.elements import CourierIssue
from courier.utils import cdata, valid_xml

CONFIG = get_config()


jinja_env = Environment(
    loader=PackageLoader('courier', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)
jinja_env.filters['valid_xml'] = valid_xml
jinja_env.filters['cdata'] = cdata


def extract_articles_from_issue(
    courier_issue: CourierIssue,
    template_name: str = CONFIG.default_template,
    extract_folder: Union[str, os.PathLike] = CONFIG.articles_dir,
) -> None:

    template = jinja_env.get_template(template_name)
    ext = template_name.split('.')[-2]

    extract_folder = Path(extract_folder) / ext
    Path(extract_folder).mkdir(parents=True, exist_ok=True)

    for i, article in enumerate(courier_issue.articles, 1):
        article_text = template.render(article=article)
        with open(
            Path(extract_folder / f'{article.courier_id}_{i:02}_{article.record_number}.{ext}'), 'w', encoding='utf-8'
        ) as fp:
            fp.write(article_text)


def extract_articles(
    input_folder: Union[str, os.PathLike] = CONFIG.xml_dir,
    article_index: pd.DataFrame = CONFIG.article_index,
    template_name: str = CONFIG.default_template,
    output_folder: Union[str, os.PathLike] = CONFIG.articles_dir,
) -> None:

    missing = set()

    for courier_id in tqdm(article_index['courier_id'].unique(), desc=f'Extracting {template_name.split(".")[-2]}'):

        filename_pattern = os.path.join(input_folder, f'{courier_id}eng*.xml')
        filename = glob.glob(filename_pattern)

        if len(filename) == 0:
            missing.add(courier_id)
            logger.warning(f'No match found for {courier_id}')
            continue

        if len(filename) > 1:
            logger.warning(f'Duplicate matches for: {courier_id}: {", ".join([f.split("/")[-1] for f in filename])}')
            continue

        extract_articles_from_issue(
            courier_issue=CourierIssue(courier_id),
            template_name=template_name,
            extract_folder=output_folder,
        )

    if len(missing) != 0:  # pragma: no cover
        logger.warning('Missing courier_ids: ', *missing)

    article_index_to_csv(article_index, output_folder)


if __name__ == '__main__':
    argh.dispatch_command(extract_articles)
