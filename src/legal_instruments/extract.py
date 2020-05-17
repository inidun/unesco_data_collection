import bs4
import re
import types
import calendar

LINK_REGEX = r"(?:(?P<City>.*?(?=,)),\s+)?(?P<Day>\d{1,2})\s+(?P<Month>\w+)\s+(?P<Year>\d{4})"
MONTH_NAMES = { v.lower(): k for k,v in enumerate(calendar.month_name) }
URL_SELECT = "table > tr > td.list > a:nth-child(1).LIST[href*='URL_ID']"

def fix_text(z):
    return " ".join(z.split())

def extract_where_and_when(info):

    parts = re.match(LINK_REGEX, info)

    return types.SimpleNamespace(
        year  = int(parts["Year"]),
        month = MONTH_NAMES[parts["Month"].lower()],
        day   = int(parts["Day"]),
        city  = parts["City"] or ""
    )

def extract_text(page):

    soup = bs4.BeautifulSoup(page, "html.parser")

    content = soup.find(class_="long_desc").get_text()

    return content

def extract_links(page, item_type):

    soup = bs4.BeautifulSoup(page, "html.parser")

    for index, item in enumerate(soup.select(URL_SELECT)):

        tag = item.parent.find("a")

        where_and_when = extract_where_and_when(tag.next_sibling.next_sibling)

        yield types.SimpleNamespace(
            id=index,
            filename="{0}_{1:03d}_{2}{3}.txt".format(
                item_type, index,
                where_and_when.year,
                '' if where_and_when.city == ""
                    else ('_' + where_and_when.city.lower().replace(' ', '_'))
            ),
            type=item_type,
            href=tag.get("href"),
            year=where_and_when.year,
            month=where_and_when.month,
            day=where_and_when.day,
            city=where_and_when.city,
            title=fix_text(tag.string),
        )
