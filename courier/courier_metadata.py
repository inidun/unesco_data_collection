import itertools
import re
from typing import List

import argh
import pandas as pd


def expand_article_pages(page_ref: str) -> List[int]:
    """['p. D-D', 'p. D', 'p. D, D ', 'p. D, D-D ', 'p.D-D', 'p.D',
    'p. D-D, D ', 'page D', 'p., D-D', 'p. D-D, D-D ']"""

    page_ref = re.sub(r"^(p\.\,?|pages?)", "", page_ref).replace(" ", "").split(",")

    ix = itertools.chain(
        *(
            [list(range(int(x), int(y) + 1)) for x, y in [w.split('-') for w in page_ref if '-' in w]]
            + [[int(x)] for x in page_ref if '-' not in x]
        )
    )

    return list(ix)


def extract_courier_id(eng_host_item: str) -> str:

    m = re.match(r".*\s(\d+)(\seng$)", eng_host_item)
    if not m:
        print(eng_host_item)
        return None

    courier_id = m.group(1)  # .replace(' ', '')
    if len(courier_id) < 6:
        courier_id = "0" + courier_id

    return courier_id


def extract_english_host_item(host_item: str) -> str:

    items = [x for x in host_item.split("|") if x.endswith("eng")]
    if len(items) == 0:
        return None

    return items[0]


# FIXME: Rename to load
def create_article_index(filename: str) -> pd.DataFrame:

    df = pd.read_csv(filename, sep=";")

    df.columns = [
        "record_number",
        "catalogue_title",
        "authors",
        "titles_in_other_languages",
        "languages",
        "series",
        "catalogue_subjects",
        "document_type",
        "host_item",
        "publication_date",
        "notes",
    ]

    df = df[df["document_type"] == "article"]
    df = df[df.languages.str.contains("eng")]

    df["eng_host_item"] = df["host_item"].apply(extract_english_host_item)
    df = df.copy()

    df["page_ref"] = df["eng_host_item"].str.extract(
        r"((?:p\.\,?|pages?)(?:\s*\d+(?:-\d+)*)(?:\,\s*\d{1,3}(?:-\d{1,3})*\s)*)"
    )[0]

    df.loc[df.record_number == 187812, "page_ref"] = "p. 18-31"
    df.loc[df.record_number == 64927, "page_ref"] = "p. 28-29"

    df["courier_id"] = df.eng_host_item.apply(extract_courier_id)
    df["pages"] = df.page_ref.apply(expand_article_pages)
    df["year"] = df.publication_date.apply(lambda x: int(x[:4]))

    return df[
        [
            "record_number",
            "catalogue_title",
            # 'authors',
            # 'titles_in_other_languages',
            # 'languages',
            # 'series',
            # 'catalogue_subjects',
            # 'document_type',
            # 'host_item',
            "eng_host_item",
            "courier_id",
            "year",
            "publication_date",
            "pages",
            "notes",
        ]
    ]


def save_article_index(input_file='UNESCO_Courier_metadata.csv', output_file='article_index.csv'):
    """Creates article index from Courier metadata file

    Args:
        input_file (str, optional): Path to courier metadata index file. Defaults to 'UNESCO_Courier_metadata.csv'.
        output_file (str, optional): Path to output article metadata file. Defaults to 'article_index.csv'.
    """

    article_index = create_article_index(input_file)
    article_index.to_csv(output_file, sep='\t')


# TODO: #17 Add command line arguments
if __name__ == "__main__":
    argh.dispatch_command(save_article_index)
