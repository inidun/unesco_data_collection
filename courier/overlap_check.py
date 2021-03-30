#%%

import pandas as pd
import ast

df = pd.read_csv("article_index.csv", sep="\t")
df = df[["courier_id", "record_number", "pages"]]

df["pages"] = df["pages"].apply(lambda x: ast.literal_eval(x))
df_pages = df.explode("pages")

page_count = df_pages.groupby(["courier_id", "pages"]).size()
page_count = page_count.reset_index()
page_count.columns = ["courier_id", "pages", "count"]

overlapping_pages = page_count[page_count["count"] > 1]
overlapping_pages = overlapping_pages.rename(columns={"pages": "page"})

overlapping_pages.to_csv("../data/courier/overlapping_pages.csv", sep="\t", index=False)

# %%
