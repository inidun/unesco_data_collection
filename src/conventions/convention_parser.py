import bs4
import re


class ConventionParser:
    def extract(self, html_text):

        soup = bs4.BeautifulSoup(html_text, "html.parser")

        content = soup.find(class_="long_desc").get_text()

        return content


class ConventionIndexParser:
    def extract(self, html_text):

        soup = bs4.BeautifulSoup(html_text, "html.parser")

        links = soup.select(
            "table > tr > td.list > a:nth-child(1).LIST[href*='URL_ID']"
        )
        data = [
            (
                y.find("a").get("href"),
                y.find("a").string,
                y.find("a").next_sibling.next_sibling,
            )
            for y in [x.parent for x in links]
        ]

        regex = (
            r"(?P<City>.*?(?=,)),\s+(?P<Day>\d{1,2})\s+(?P<Month>\w+)\s+(?P<Year>\d{4})"
        )

        matches = [
            (y["Year"], y["Day"], y["Month"], y["City"], z[0], z[1], z[2])
            for y, z in [(re.match(regex, x[2]), x) for x in data]
        ]

        return matches
