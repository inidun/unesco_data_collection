# unesco_data_collection
Script and code related to collecting and curating UNESCO data.


### Changelog (branch: `courier`)

- Updated Python from 3.7 to 3.8
- Using `poetry` instead of `pipenv`
- Restructured project to reflect `poetry`'s standard structure
- Updated `legal_instruments` code to reflect new project structure
- Removed unused dependencies
- Removed deprecated data files (Have been moved to other repo)
- Added `courier` module
- Added `courier` data folder


## Courier

Code related to extracting and curating data for the Courier corpus.

### Extracting with PDFBox

__Prerequisites:__

- Java. Must be in path.

__Usage:__

    extract_text_pdfbox.py [-h] files output-folder

### Extracting with Tesseract

__Prerequisites:__

- Poppler. Install with: `sudo apt install poppler-utils`
- Tesseract OCR. Install with: `sudo apt install tesseract-ocr`

__Usage:__

    extract_text_tesseract.py [-h] [--first-page FIRST_PAGE] [-l LAST_PAGE] [-d DPI] [--fmt FMT] files output-folder


### Notes

Mismatch in index: Some PDF-files have double pages. This leads to article overlap.

__PDFBox unable to extract text from:__

    132107engb

__In index but files missing:__

    059709eng
    124785eng
    367693eng
    370032eng
    370977eng
    372603eng
    373788eng

__Current corpus stats:__

	in metadata index   8313
	 - of type article  7639
	 - in english       7612
    Output              7505
    Missing             107

__TODO:__

- [ ] Missing pages
- [ ] Double page exclusions
- [ ] Article overlap
- [ ] ...

## Legal instruments

Script and code related to collecting (scraping) SSI (legal instruments) corpus data from the UNESCO website. This is the first of three text corpora of UNESCO documents.

### Main loop:

```python
index = GetIndexUrls()
for item in index:
    pageHtml = getHtmlPage(index.url)
    conventionText = ConventionParser().extract(pageHtml)
    storeText(genFilename(item), conventionText)
```