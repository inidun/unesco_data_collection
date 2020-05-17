import sys
import os

def project_root():
    folder = os.getcwd()
    while os.path.split(folder)[1] not in ('', 'unesco_data_collection'):
        folder, _ = os.path.split(folder)
    return folder

sys.path.append(project_root())

from src.legal_instruments.pipeline import Pipeline
import src.legal_instruments.tasks as task

def collect_legal_instruments():

    url_index = [
        ('http://portal.unesco.org/en/ev.php-URL_ID=12025&URL_DO=DO_TOPIC&URL_SECTION=-471.html', 'CONVENTION'),
        ('http://portal.unesco.org/en/ev.php-URL_ID=12026&URL_DO=DO_TOPIC&URL_SECTION=-471.html', 'RECOMMENDATION'),
        ('http://portal.unesco.org/en/ev.php-URL_ID=12027&URL_DO=DO_TOPIC&URL_SECTION=-471.html', 'DECLARATION')
    ]

    pipeline = Pipeline()\
        .add(task.scrape_pages)\
        .add(task.extract_links)\
        .add(task.extract_text)\
        .add(task.progress)\
        .add(task.store_text, os.path.join(project_root(), "data", "legal_instrument_corpus.txt.zip"))\
        .add(task.store_index, os.path.join(project_root(), "data", "legal_instrument_index.csv"))

    df = pipeline.apply(url_index)

    print(df)

if __name__ == "__main__":
    collect_legal_instruments()
