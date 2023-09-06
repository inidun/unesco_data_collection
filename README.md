# unesco_data_collection
Scripts and code related to collecting and curating the UNESCO Courier corpus.

## Scripts
### Export tagged issues

	python courier/elements/export_tagged_issues.py


### Extract articles from tagged issues 

	python courier/cli/tagged2article.py

```bash
Usage: tagged2article.py [OPTIONS] SOURCE TARGET_FOLDER [ARTICLE_INDEX]

Options:
  --editorials / --no-editorials
  --supplements / --no-supplements
  --unindexed / --no-unindexed
```

### Generate corpus report

    python courier/scripts/corpus_report.py [OUTPUT_FOLDER]


### Extract raw issue and page corpora

	python courier/corpora.py

### Find double spreads/centerfolds in PDFs

    find_double_pages.sh <dir>


### Deprecated

#### Generate overlapping article statistics

	python courier/split_article_pages.py

```bash
usage: split_article_pages.py [-h] [-o OUTPUT_FOLDER] [--match-function {regex,fuzzywuzzy}]

options:
  -o OUTPUT_FOLDER, --output-folder 	OUTPUT_FOLDER
  --match-function {regex,fuzzywuzzy}	'regex'
```

#### Export articles

	courier/elements/export_articles.py

