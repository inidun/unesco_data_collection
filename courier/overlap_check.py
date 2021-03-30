#%%
import pandas as pd
import ast

df = pd.read_csv("../data/courier/article_index.csv", sep="\t")
df = df[["courier_id", "record_number", "pages"]]

df["pages"] = df["pages"].apply(lambda x: ast.literal_eval(x))
df_pages = df.explode("pages")

page_count = df_pages.groupby(["courier_id", "pages"]).size()
page_count = page_count.reset_index()
page_count.columns = ["courier_id", "pages", "count"]

overlapping_pages = page_count[page_count["count"] > 1]
overlapping_pages = overlapping_pages.rename(columns={"pages": "page"})


def save_overlapping_pages(overlap_df: pd.DataFrame) -> None:
    overlap_df.to_csv("../data/courier/overlapping_pages.csv", sep="\t", index=False)


# save_overlapping_pages(overlapping_pages)


#%% TEMP STUFF

# d = overlapping_pages["copy"] = overlapping_pages.apply(lambda x: f'cp {x["courier_id"]:06}eng?_{x["page"]:04}.txt ./tmp', axis=1)
# d.to_csv("copy.sh", index=False)

# df_org = pd.read_csv("../data/courier/article_index.csv", sep="\t")
# df_org["record_number"].unique
