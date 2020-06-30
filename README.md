# unesco_data_collection
Script and code related to collecting data (scraping) from the UNESCO website

This is the first of three text corpora of UNESCO documents.

### Main loop:

```python
index = GetIndexUrls()
for item in index:
    pageHtml = getHtmlPage(index.url)
    conventionText = ConventionParser().extract(pageHtml)
    storeText(genFilename(item), conventionText)
```