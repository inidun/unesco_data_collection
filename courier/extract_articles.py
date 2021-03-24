# %%

import glob
import io
import os
import re
import sys
from typing import Dict, List

import pandas as pd
import untangle
from jinja2 import Environment, PackageLoader, select_autoescape

sys.path.insert(0, "~/source/inidun/unesco_data_collection/")

from courier.courier_metadata import create_article_index
from courier.elements import CourierIssue

jinja_env = Environment(
    loader=PackageLoader("courier", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)

remove_re = re.compile("[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]")
data_folder = "./data/courier/articles"


def read_xml(filename: str) -> untangle.Element:
    with open(filename, "r") as fp:
        content = fp.read()
        content = remove_re.sub("", content)
        xml = io.StringIO(content)
        element = untangle.parse(xml)
        return element


# TODO: add template as argument
def extract_articles_from_issue(courier_issue: CourierIssue) -> None:

    template = jinja_env.get_template("article.xml.jinja")

    for i, article in enumerate(courier_issue.articles, 1):
        # print(f"Processing {article.record_number}")
        article_text = template.render(article=article)
        with open(
            os.path.join(
                data_folder, f"{article.courier_id}_{i:02}_{article.record_number}.xml"
            ),
            "w",
        ) as fp:
            fp.write(article_text)


def extract_articles(folder: str, index: pd.DataFrame, landscape_pages: str) -> None:

    missing = set()

    for issue in index["courier_id"].unique():  # FIXME: remove head

        filename_pattern = os.path.join(folder, f"{issue}eng*.xml")
        filename = glob.glob(filename_pattern)

        if len(filename) == 0:
            missing.add(issue)
            print(f"no match for {issue}")
            continue

        if len(filename) > 1:
            print(f"Duplicate matches for: {issue}")
            continue

        # FIXME: only call read_xml when necessary
        try:
            extract_articles_from_issue(
                CourierIssue(
                    index.loc[index["courier_id"] == issue],
                    read_xml(filename[0]),
                    landscape_pages.get(issue, []),
                )
            )
        except Exception as e:
            print(filename[0], e)

        # extract_articles_from_issue(filename, index.loc[index["courier_id"] == issue])
        # TODO: Check pages for possible mismatch
        # TODO: Check overlapping pages

    print("Missing courier_ids: ", *missing)


def find_article_titles(folder: str, index: pd.DataFrame, landscape_pages: str) -> List:

    items = []

    for issue in index["courier_id"].unique():

        filename_pattern = os.path.join(folder, f"{issue}eng*.xml")
        filename = glob.glob(filename_pattern)

        if len(filename) == 0:
            print(f"no match for {issue}")
            continue

        if len(filename) > 1:
            print(f"Duplicate matches for: {issue}")
            continue

        courier_issue = CourierIssue(
            index.loc[index["courier_id"] == issue],
            read_xml(filename[0]),
            landscape_pages.get(issue, [])
        )

        for article in courier_issue.articles:

            try:

                expr = create_regexp(article.title)

                page_numbers = courier_issue.find_pattern(expr)

                items.append(
                    {
                        "title": article.title,
                        "courier_id": article.courier_id,
                        "record_number": article.record_number,
                        "page_numbers": page_numbers,
                    }
                )

            except:
                pass

    df = pd.DataFrame(items)
    df.to_csv("./data/article_titles.csv", sep="\t")

    return items


def create_regexp(title):

    tokens = re.findall("[a-zåäö]+", title.lower())
    expr = "[^a-zåäö]+".join(tokens)

    return expr[1:]


def read_landscape_pages(filename: str) -> Dict:
    with open(filename, "r") as fp:
        data = fp.readlines()
        pages = {
            os.path.basename(x)[:6]: list(map(int, x.split(" ")[1:])) for x in data
        }
    return pages


def main():
    article_index = create_article_index("./data/UNESCO_Courier_metadata.csv")
    landscape_pages = read_landscape_pages("./courier/landscape_pages.txt")
    extract_articles("./data/courier/xml", article_index, landscape_pages)
    # find_article_titles("./data/courier/xml", article_index)


if __name__ == "__main__":
    main()
