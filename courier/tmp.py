#%%
from jinja2 import Environment, PackageLoader, select_autoescape
import untangle
import courier_metadata

# %%

article_index = courier_metadata.create_article_index('UNESCO_Courier_metadata.csv')

env = Environment(
    loader=PackageLoader('courier', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)

template = env.get_template('article.xml.jinja')
env.list_templates()

# %%
courier_issue = untangle.parse("../data/courier/xml/012656engo.xml")

# %%
# courier_issue.document["id"]
print(courier_issue.document.page[0].cdata)
# print(courier_issue.document.page[0]["number"])
# %%
print(template.render(data=courier_issue, start=0, stop=2))
# %%

# %%

# %%
# [x["number"] for x in courier_issue.document.page]
# [x.cdata for x in courier_issue.document.page]
# print(courier_issue.document.page)

# %%


