import sys
import os
from datetime import date

def project_root():
    folder = os.getcwd()
    while os.path.split(folder)[1] not in ('', 'unesco_data_collection'):
        folder, _ = os.path.split(folder)
    return folder

sys.path.append(project_root())

from src.legal_instruments.pipeline import Pipeline
import src.legal_instruments.tasks as task
import src.legal_instruments.extract as extract

def collect_legal_instruments():

    corpus_filename = os.path.join(project_root(), "data", "legal_instrument_corpus.txt.zip")
    index_filename = os.path.join(project_root(), "data", "legal_instrument_index.csv")

    legal_instrument_urls = [
        ('http://portal.unesco.org/en/ev.php-URL_ID=12025&URL_DO=DO_TOPIC&URL_SECTION=-471.html', 'CONVENTION'),
        ('http://portal.unesco.org/en/ev.php-URL_ID=12026&URL_DO=DO_TOPIC&URL_SECTION=-471.html', 'RECOMMENDATION'),
        ('http://portal.unesco.org/en/ev.php-URL_ID=12027&URL_DO=DO_TOPIC&URL_SECTION=-471.html', 'DECLARATION')
    ]

    constitution = extract.create_item(
        "CONSTITUTION", "ev.php-URL_ID=15244&URL_DO=DO_TOPIC&URL_SECTION=201.html",
        date(1945, 11, 16), "London", "UNESCO Constitution"
    )

    pipeline = Pipeline()\
        .add(task.extract_pages)\
        .add(task.extract_items, constitution)\
        .add(task.extract_text)\
        .add(task.progress)\
        .add(task.store_text, corpus_filename)\
        .add(task.store_index, index_filename)

    df = pipeline.apply(legal_instrument_urls)

    print(df)

if __name__ == "__main__":
    collect_legal_instruments()
