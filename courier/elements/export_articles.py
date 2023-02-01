# pylint: disable=redefined-outer-name
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from loguru import logger

from courier.article_index import article_index_to_csv
from courier.config import get_config
from courier.elements.assign_page_service import AssignPageService
from courier.elements.consolidate_text_service import ConsolidateTextService
from courier.elements.elements import CourierIssue
from courier.elements.statistics import IssueStatistics
from courier.utils.logging import file_logger

CONFIG = get_config()


def export_articles(
    courier_id: str,
    export_folder: Union[str, os.PathLike] = CONFIG.articles_dir / 'exported',
) -> List[Dict[str, Any]]:
    def dipatch_articles(export_folder: Union[str, os.PathLike], issue: CourierIssue) -> None:
        Path(export_folder).mkdir(parents=True, exist_ok=True)
        for article in issue.articles:
            if article.catalogue_title is None:
                continue
            filename: Path = Path(export_folder) / article.filename
            with file_logger(Path(export_folder) / 'extract_log.csv', format='{message}', level='TRACE') as logfile:
                logfile.trace(article.record)
            with open(filename, 'w', encoding='utf-8') as fp:
                fp.write(article.get_text())

    issue: CourierIssue = CourierIssue(courier_id)
    AssignPageService().assign(issue)
    ConsolidateTextService().consolidate(issue)
    dipatch_articles(export_folder, issue)

    return IssueStatistics(issue).errors


def save_overlap(statistics: pd.DataFrame, filename: Optional[Union[str, os.PathLike]] = None) -> pd.DataFrame:
    statistics['case'] = statistics.case.astype('str')
    overlap = (
        statistics.groupby(['courier_id', 'page'])['case']
        .agg(['count', ','.join])
        .reset_index()
        .rename(columns={'join': 'cases'})
    )
    overlap['courier_id'] = overlap.courier_id.astype('int')

    # TODO: to_csv params
    if filename is not None:
        overlap.to_csv(filename, sep='\t', index=False, quoting=csv.QUOTE_NONNUMERIC)
    return overlap


def save_statistics(statistics: pd.DataFrame, filename: Union[str, os.PathLike]) -> None:
    statistics['case'] = statistics.case.astype('str')
    stat_groups = statistics.groupby('case')
    with pd.ExcelWriter(filename) as writer:  # pylint: disable=abstract-class-instantiated
        for key, _ in stat_groups:
            stat_groups.get_group(key).to_excel(writer, sheet_name=key, index=False)


def save_statistics_by_case(statistics: pd.DataFrame, folder: Union[str, os.PathLike]) -> None:
    for k, v in statistics.groupby('case'):
        v.to_csv(Path(folder) / f'stats_case{k}.csv', sep=';', index=False, quoting=csv.QUOTE_NONNUMERIC)


def extract_percentage(filename: Union[str, os.PathLike]) -> float:
    df = pd.read_csv(filename, sep=';')
    complete_ratio = np.count_nonzero(df.assigned == df.total) / len(df)  # pylint: disable=no-member
    return complete_ratio


def main() -> None:
    export_folder: Path = CONFIG.articles_dir / f'exported_{datetime.now().strftime("%Y-%m-%dT%H%M")}'
    article_index_to_csv(CONFIG.article_index, export_folder)
    stats: List[Dict[str, Any]] = []

    with open(Path(export_folder) / 'extract_log.csv', 'w', encoding='utf8') as fp:
        fp.write('courier_id;year;record_number;assigned;not_found;total\n')

    courier_ids = [x[:6] for x in CONFIG.get_courier_ids()]
    for courier_id in courier_ids:
        try:
            stats += export_articles(courier_id, export_folder)
        except ValueError as e:
            logger.info(e)

    statistics = (
        pd.DataFrame(stats)
        .drop(columns=['article'])
        .sort_values(by=['year', 'courier_id', 'record_number', 'page', 'case'])
    )
    statistics['case'] = statistics.case.astype('str')

    save_overlap(statistics, Path(export_folder) / 'overlap.csv')
    save_statistics(statistics, Path(export_folder) / 'stats.xlsx')
    save_statistics_by_case(statistics, Path(export_folder))

    with file_logger(Path(export_folder) / 'extract_percentage.log', format='{message}', level='INFO') as logfile:
        percentage = extract_percentage(Path(export_folder) / 'extract_log.csv')
        logfile.info(f'Articles completely extracted: {percentage*100:.2f}%')


if __name__ == '__main__':
    main()
