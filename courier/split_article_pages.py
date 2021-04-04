# %%
import glob
import os
import re

import pandas as pd

from courier.config import CourierConfig
from courier.courier_metadata import create_article_index
from courier.overlap_check import get_overlapping_pages

CONFIG = CourierConfig()


def create_regexp(title_string: str) -> str:
    tokens = re.findall("[a-zåäö]+", title_string.lower())
    expression = "[^a-zåäö]+".join(tokens)
    return expression[1:]


# FIXME: Encapsulate in function, otherwise import and testing is slow
# FIXME: Get article index from config!!
article_index = create_article_index(CONFIG.courier_metadata)
double_pages = CONFIG.double_pages

df_overlap = get_overlapping_pages(article_index)

found_stats = []

for row in df_overlap.to_dict("records"):  # removed orient=

    articles_on_page = article_index[
        (article_index.courier_id == row["courier_id"]) & article_index.pages.apply(lambda x, r=row: r["page"] in x)
    ]

    if row["count"] != len(articles_on_page):
        print(f'Page count mismatch: {row["courier_id"]}')

    articles_on_page = articles_on_page.to_dict("records")  # removed orient=

    page_delta = len([x for x in double_pages.get(row["courier_id"], []) if x < row["page"]])
    row_page = row["page"] - page_delta

    page_filename_pattern = f'{int(row["courier_id"]):06}eng*_{row_page:04}.txt'
    page_filenames = glob.glob(os.path.join(CONFIG.pdfbox_txt_dir, page_filename_pattern))

    if len(page_filenames) == 0:
        print(f'no match for {row["courier_id"]}')
        continue
    if len(page_filenames) > 1:
        print(f'Duplicate matches for: {row["courier_id"]}')
        continue

    with open(page_filenames[0], "r") as fp:
        page_text = fp.read()

    page_stat = dict(row)
    page_stat["page_corr"] = row_page
    page_stat["found"] = 0
    page_stat["not_found"] = 0

    for article_info in articles_on_page:
        title = article_info["catalogue_title"]
        expr = create_regexp(title)

        # TODO: More fuzzy, or keyword in context
        m = re.search(expr, page_text, re.IGNORECASE)
        if m:
            # print(f"Found     {title}")
            page_stat["found"] += 1
        else:
            # print(f"Not Found {title}")
            page_stat["not_found"] += 1

    found_stats.append(page_stat)

pd.DataFrame(found_stats).to_csv(
    os.path.join(CONFIG.project_root, "data/courier/overlap_match_stats.csv"), index=False, sep="\t"
)

# %%


def main():
    pass


if __name__ == "__main__":
    main()

# %%
