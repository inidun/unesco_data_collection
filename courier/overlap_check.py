import pandas as pd
import ast

from courier.courier_metadata import create_article_index

df = create_article_index("../data/courier/UNESCO_Courier_metadata.csv")
df = df[["courier_id", "record_number", "pages"]]

df["pages"] = df["pages"].apply(lambda x: ast.literal_eval(str(x)))
df_pages = df.explode("pages")

page_count = df_pages.groupby(["courier_id", "pages"]).size()
page_count = page_count.reset_index()
page_count.columns = ["courier_id", "pages", "count"]

overlapping_pages = page_count[page_count["count"] > 1]
overlapping_pages = overlapping_pages.rename(columns={"pages": "page"})

def save_overlapping_pages(overlap_df: pd.DataFrame) -> None:
    overlap_df.to_csv("../data/courier/overlapping_pages.csv", sep="\t", index=False)

def create_copy_script(overlap_df: pd.DataFrame) -> None:
    overlap_df["copy"] = overlap_df.apply(lambda x: f'cp {int(x["courier_id"]):06}eng?_{x["page"]:04}.txt ./tmp', axis=1)
    d = overlap_df["copy"]
    d.to_csv("copy.sh", index=False)

# save_overlapping_pages(overlapping_pages)
# create_copy_script(overlapping_pages)

# MISSING - Becasuse pdf-sources are missing
# 372603eng*_0012.txt'
# 367693eng*_0018.txt'
# 059709eng*_0024.txt'
# 059709eng*_0011.txt'
# 059709eng*_0007.txt'
