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

### Changelog

- Updated Python from 3.7 to 3.8
- Using poetry instead of pipenv
- Restructured project to reflect poetry's standard structure
- Updated `legal_instruments` code to reflect new project structure
- Removed unused dependencies
- Removed deprecated data files (Have been moved to other repo)
- Added Courier module
- Added Courier data