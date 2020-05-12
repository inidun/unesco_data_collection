import bs4

class ConventionParser():

    def extract(self, html_text):

        soup = bs4.BeautifulSoup(html_text, "html.parser")

        content = soup.find(class_="long_desc").get_text()

        return None
