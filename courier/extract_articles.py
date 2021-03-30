import glob
import io
import os
import re
import csv

from typing import Dict, List

import pandas as pd
import untangle
from jinja2 import Environment, PackageLoader, select_autoescape

from courier.courier_metadata import create_article_index
from courier.elements import CourierIssue

# TODO: Move to config file
# EXCLUDED_DOUBLE_PAGES = ["033144", "110425", "074589"]
DEFAULT_OUTPUT_FOLDER = "../data/courier/articles"
DEFAULT_TEMPLATE_NAME = "article.xml.jinja"
DOUBLE_PAGES_FILE = "../data/courier/double_pages/double_pages.txt"
EXCLUSIONS_FILE = "../data/courier/double_pages/exclude.txt"
METADATA_FILE = "../data/courier/UNESCO_Courier_metadata.csv"
REMOVE_RE = re.compile("[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]")
XML_INPUT_FOLDER = "../data/courier/input/xml"


jinja_env = Environment(
    loader=PackageLoader("courier", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def read_xml(filename: str) -> untangle.Element:
    with open(filename, "r") as fp:
        content = fp.read()
        content = REMOVE_RE.sub("", content)
        xml = io.StringIO(content)
        element = untangle.parse(xml)
        return element


def extract_articles_from_issue(
    courier_issue: CourierIssue, template_name: str = None, output_folder: str = None
) -> None:

    template_name = template_name or DEFAULT_TEMPLATE_NAME
    template = jinja_env.get_template(template_name)
    ext = template_name.split(".")[-2]

    output_folder = output_folder or DEFAULT_OUTPUT_FOLDER
    os.makedirs(output_folder, exist_ok=True)

    for i, article in enumerate(courier_issue.articles, 1):
        # print(f"Processing {article.record_number}")
        article_text = template.render(article=article)
        with open(os.path.join(output_folder, f"{article.courier_id}_{i:02}_{article.record_number}.{ext}"), "w") as fp:
            fp.write(article_text)


def extract_articles(xml_input_folder: str, article_index: pd.DataFrame, double_pages: dict) -> None:

    missing = set()

    for issue in article_index["courier_id"].unique():

        filename_pattern = os.path.join(xml_input_folder, f"{issue}eng*.xml")
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
                CourierIssue(
                    article_index.loc[article_index["courier_id"] == issue],
                    read_xml(filename[0]),
                    double_pages.get(issue, []),
                )
            )
        except Exception as e:
            print(filename[0], e)

    print("Missing courier_ids: ", *missing)


def create_regexp(title: str) -> str:
    tokens = re.findall("[a-zåäö]+", title.lower())
    expr = "[^a-zåäö]+".join(tokens)
    return expr[1:]


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


def read_exclusions_from_file(filename: str) -> list:
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter=';')
        exclusions = [x[0] for x in reader]
    return exclusions


# FIXME: #23 Exclude non double pages
def read_double_pages_from_file(double_pages_file: str, exclusions_file: str) -> Dict:

    exclude = read_exclusions_from_file(exclusions_file)
    with open(double_pages_file, "r") as fp:
        data = fp.readlines()
        filtered_data = [line for line in data if all(e not in line for e in exclude)]
        pages = {os.path.basename(line)[:6]: list(map(int, line.split(" ")[1:])) for line in filtered_data}
    return pages


def main():
    article_index = create_article_index(METADATA_FILE)

    os.makedirs(DEFAULT_OUTPUT_FOLDER, exist_ok=True)
    article_index.to_csv(os.path.join(DEFAULT_OUTPUT_FOLDER, "article_index.csv"), sep="\t", index=False)

    double_pages = read_double_pages_from_file(DOUBLE_PAGES_FILE, EXCLUSIONS_FILE)

    # FIXME: FIX indata - input folder containing courier issues in xml-format
    extract_articles(XML_INPUT_FOLDER, article_index, double_pages)
    # find_article_titles("./data/courier/xml", article_index)


if __name__ == "__main__":
    main()
