import bs4
import re
import types
import calendar
import datetime

INFO_REGEX = r"(?:(?P<City>.*?(?=,)),\s+)?(?P<Day>\d{1,2})\s+(?P<Month>\w+)\s+(?P<Year>\d{4})"
LINK_REGEX = r'(?:.*?(?=URL_ID))URL_ID=(?P<unesco_id>\d+)(?:.*?(?=URL_SECTION))URL_SECTION=-?(?P<section_id>\d+).*'
MONTH_NAMES = { v.lower(): k for k,v in enumerate(calendar.month_name) }
URL_SELECT = "table > tr > td.list > a:nth-child(1).LIST[href*='URL_ID']"

def fix_text(z):
    return " ".join(z.split())

def extract_where_and_when(info):

    parts = re.match(INFO_REGEX, info)

    year = int(parts["Year"])
    month = MONTH_NAMES[parts["Month"].lower()]
    day = int(parts["Day"])
    city = parts["City"] or ""

    return datetime.date(year=year, month=month, day=day), city

def extract_unesco_ids(href):

    parts = re.match(LINK_REGEX, href)

    return int(parts["section_id"]), int(parts["unesco_id"])

def extract_text(page):

    soup = bs4.BeautifulSoup(page, "html.parser")

    content = soup.find(class_="long_desc").get_text()

    return content

def extract_items(page, item_type):

    soup = bs4.BeautifulSoup(page, "html.parser")

    for element in soup.select(URL_SELECT):

        tag = element.parent.find("a")

        date, city = extract_where_and_when(tag.next_sibling.next_sibling)

        yield create_item(item_type, tag.get("href"), date, city, fix_text(tag.string))

def create_item(item_type, href, sign_date, city, title):

    section_id, unesco_id = extract_unesco_ids(href)

    _city = "" if city == ""  else ('_' + city.lower().replace(' ', '_'))

    return types.SimpleNamespace(
        type=item_type,
        section_id=section_id,
        unesco_id=unesco_id,
        href=href,
        date=sign_date,
        city=city,
        title=title,
        filename="{0}_{1:04d}_{2:06d}_{3}{4}.txt".format(item_type, section_id, unesco_id, sign_date.year, _city),
    )
