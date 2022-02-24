import io
import os
from typing import Union

import untangle

from courier.config import get_config
from courier.extract.java_extractor import ExtractedPage, ExtractedPages, JavaExtractor
from courier.utils import valid_xml

CONFIG = get_config()


def get_pdf_issue_content(courier_id: str) -> ExtractedPages:
    extractor: JavaExtractor = JavaExtractor()
    filename: str = str(list(CONFIG.pdf_dir.glob(f'{courier_id}*.pdf'))[0])
    issue: ExtractedPages = extractor.extract_pages(filename)
    return issue


def read_xml(filename: Union[str, bytes, os.PathLike]) -> untangle.Element:
    with open(filename, 'r', encoding='utf-8') as fp:
        content = fp.read()
        content = valid_xml(content)
        xml = io.StringIO(content)
        element = untangle.parse(xml)
        return element


# NOTE: Needed for test discovery (WIP). Remove later if deemed deprecated.
def get_xml_issue_content(courier_id: str) -> ExtractedPages:

    if len(courier_id) != 6:
        raise ValueError(f'Not a valid courier id "{courier_id}')
    if courier_id not in CONFIG.article_index.courier_id.values:
        raise ValueError(f'{courier_id} not in article index')

    untangle_element = read_xml(list(CONFIG.xml_dir.glob(f'{courier_id}*.xml'))[0])
    pages = []
    for pdf_page_number, content in enumerate(untangle_element.document.page, 1):
        page: ExtractedPage = ExtractedPage(pdf_page_number=pdf_page_number, content=content, titles=[])
        pages.append(page)

    issue: ExtractedPages = ExtractedPages(pages=pages)
    return issue


if __name__ == '__main__':
    pass
