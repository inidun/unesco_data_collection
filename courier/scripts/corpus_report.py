# pylint: disable=redefined-outer-name
from typing import Any

import argh
import pandas as pd
from loguru import logger

from courier.article_index import article_index_to_csv
from courier.config import get_config
from courier.elements.assign_page_service import AssignPageService
from courier.elements.consolidate_text_service import ConsolidateTextService
from courier.elements.elements import CourierIssue
from courier.elements.statistics import IssueStatistics

CONFIG = get_config()


def get_issue_report(courier_id: str) -> tuple[list[dict[str, Any]], list[str]]:
    issue: CourierIssue = CourierIssue(courier_id)
    AssignPageService().assign(issue)
    ConsolidateTextService().consolidate(issue)

    aricle_records = []
    for article in issue.articles:
        if article.catalogue_title is None:
            logger.info(f'Article {article.record} has no catalogue title')
            continue
        aricle_records.append(article.record)

    return IssueStatistics(issue).errors, aricle_records


def get_corpus_report(courier_ids: list[str]) -> tuple[pd.DataFrame, list[str]]:
    reports: list[dict[str, Any]] = []
    records: list[str] = []

    # get report and article records for each issue
    for courier_id in courier_ids:
        try:
            reports.extend(get_issue_report(courier_id)[0])
            records.extend(get_issue_report(courier_id)[1])
        except ValueError as e:
            logger.error(f'Error processing issue {courier_id}: {e}')

    corpus_report = (
        pd.DataFrame(reports)
        .drop(columns=['article'])
        .sort_values(by=['year', 'courier_id', 'record_number', 'page', 'case'])
    )
    # cast case to string to avoid scientific notation
    corpus_report['case'] = corpus_report.case.astype('str')

    return corpus_report, records


def report_to_excel(reports: pd.DataFrame, output_folder: str) -> None:
    filename = f'{output_folder}/assignment_errors.xlsx'

    with pd.ExcelWriter(filename) as writer:  # pylint: disable=abstract-class-instantiated
        reports.to_excel(writer, sheet_name='all', index=False)
        # group by case
        case_groups = reports.groupby('case')
        # save each case to a separate sheet
        for case, group in case_groups:
            group.to_excel(writer, sheet_name=f'case_{case}', index=False)

    # save overlapping articles to a separate file
    overlap_file = f'{output_folder}/page_overlaps.xlsx'
    overlapping_cases = (
        reports.groupby(['year', 'courier_id', 'page'])['case']
        .agg(['count', lambda x: ','.join(x.unique())])
        .reset_index()
    )
    overlapping_cases.columns = ['year', 'courier_id', 'page', 'overlap_count', 'case_list']
    overlapping_cases = overlapping_cases.sort_values(by=['year', 'courier_id', 'page'])
    overlapping_cases = overlapping_cases[['courier_id', 'page', 'overlap_count', 'case_list', 'year']]
    overlapping_cases.to_excel(overlap_file, sheet_name='overlap', index=False)


def save_article_records(output_folder: str, records: list[str], output_format: str = 'excel') -> None:
    records_columns = ['courier_id', 'year', 'record_number', 'assigned', 'not_found', 'total']
    records_df = pd.DataFrame([x.split(';') for x in records], columns=records_columns)
    records_df = records_df.astype(
        {'year': 'int', 'record_number': 'int', 'assigned': 'int', 'not_found': 'int', 'total': 'int'}
    )

    # percentage of issues with all articles assigned
    percentage = records_df.apply(lambda x: x.assigned == x.total, axis=1).value_counts()[True] / len(records_df) * 100
    logger.info(f'{percentage:.2f}% of issues have all articles assigned')
    # save text file with percentage of assigned articles
    with open(f'{output_folder}/assigned.txt', 'w', encoding='utf-8') as f:
        f.write(f'{percentage:.2f}% of issues have all articles assigned')

    if output_format == 'excel':
        records_df.to_excel(f'{output_folder}/article_assignment.xlsx', index=False, sheet_name='records')
    elif output_format == 'csv':
        records_df.to_csv(f'{output_folder}/article_assignment.csv', index=False, encoding='utf-8-sig')
    elif output_format == 'tsv':
        records_df.to_csv(f'{output_folder}/article_assignment.tsv', index=False, sep='\t', encoding='utf-8-sig')
    else:
        raise ValueError(f'Unknown output format {output_format}')


def main(output_folder: str) -> None:
    article_index_to_csv(CONFIG.article_index, output_folder)

    courier_ids: list[str] = [
        str(x[:6]) for x in CONFIG.get_courier_ids() if x[:6] in CONFIG.article_index.courier_id.values
    ]
    corpus_report, records = get_corpus_report(courier_ids)

    report_to_excel(corpus_report, output_folder)
    save_article_records(output_folder, records, output_format='excel')


if __name__ == '__main__':
    argh.dispatch_command(main)
