# unesco_data_collection
Script and code related to collecting and curating UNESCO data.

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


__Current corpus stats:__

    Documents:			671
    Artcles:
	in metadata index		8313
    	 - of type article	7639
    	 - in english		7612
    Pages:				27336


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