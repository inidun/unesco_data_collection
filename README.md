# unesco_data_collection
Script and code related to collecting data (scraping) from the UNESCO website


### Main loop:

```python
index = GetIndexUrls()
for item in index:
    pageHtml = getHtmlPage(index.url)
    conventionText = ConventionParser().extract(pageHtml)
    storeText(genFilename(item), conventionText)
```