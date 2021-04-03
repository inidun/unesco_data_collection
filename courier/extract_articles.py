import glob
import io
import os
import re
from typing import List, Union

import pandas as pd
import untangle
from jinja2 import Environment, PackageLoader, select_autoescape

from courier.config import CourierConfig
from courier.courier_metadata import create_article_index
from courier.elements import CourierIssue

CONFIG = CourierConfig()


jinja_env = Environment(
    loader=PackageLoader("courier", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def read_xml(filename: Union[str, bytes, os.PathLike]) -> untangle.Element:
    with open(filename, "r") as fp:
        content = fp.read()
        content = CONFIG.invalid_chars.sub("", content)
        xml = io.StringIO(content)
        element = untangle.parse(xml)
        return element


def extract_articles_from_issue(
    courier_issue: CourierIssue, template_name: str = None, output_folder: str = None
) -> None:

    template_name = template_name or CONFIG.default_template
    template = jinja_env.get_template(template_name)
    ext = template_name.split(".")[-2]

    output_folder = output_folder or CONFIG.default_output_dir
    os.makedirs(output_folder, exist_ok=True)

    for i, article in enumerate(courier_issue.articles, 1):
        # print(f"Processing {article.record_number}")
        article_text = template.render(article=article)
        with open(os.path.join(output_folder, f"{article.courier_id}_{i:02}_{article.record_number}.{ext}"), "w") as fp:
            fp.write(article_text)


def extract_articles(
    input_folder: str,
    article_index: pd.DataFrame,
    double_pages: dict,
    template_name: str = None,
    output_folder: str = None,
) -> None:

    missing = set()

    for issue in article_index["courier_id"].unique():

        filename_pattern = os.path.join(input_folder, f"{issue}eng*.xml")
        filename = glob.glob(filename_pattern)

        if len(filename) == 0:
            missing.add(issue)
            print(f"no match for {issue}")
            continue

        if len(filename) > 1:
            print(f"Duplicate matches for: {issue}")
            continue

        try:
            extract_articles_from_issue(
                courier_issue=CourierIssue(
                    article_index.loc[article_index["courier_id"] == issue],
                    read_xml(filename[0]),
                    double_pages.get(issue, []),
                ),
                template_name=template_name,
                output_folder=output_folder,
            )
        except Exception as e:
            print(filename[0], e)

    print("Missing courier_ids: ", *missing)


# FIXME Move maybe
def create_regexp(title: str) -> str:
    tokens = re.findall("[a-zåäö]+", title.lower())
    expr = "[^a-zåäö]+".join(tokens)
    return expr[1:]


# FIXME Move
def find_article_titles(folder: str, index: pd.DataFrame, double_pages: dict) -> List:

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
            index.loc[index["courier_id"] == issue], read_xml(filename[0]), double_pages.get(issue, [])
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
            except Exception as e:
                print(filename[0], e)

    df = pd.DataFrame(items)
    df.to_csv("../courier/data/article_titles.csv", sep="\t")
    return items


def main():
    article_index = create_article_index(CONFIG.courier_metadata)

    os.makedirs(CONFIG.default_output_dir, exist_ok=True)
    article_index.to_csv(os.path.join(CONFIG.default_output_dir, "article_index.csv"), sep="\t", index=False)
    extract_articles(CONFIG.pdfbox_xml_dir, article_index, CONFIG.double_pages)

    # extract_articles(CONFIG.pdfbox_xml_dir, article_index, CONFIG.double_pages, template_name="article.txt.jinja", output_folder="../data/courier/articles/txt")
    # find_article_titles("./data/courier/xml", article_index)


if __name__ == "__main__":
    main()
