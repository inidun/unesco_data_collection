# Changelog

- Updated Python from 3.7 to 3.8
- Using poetry instead of pipenv
- Restructured project to reflect poetry's standard structure
- Updated `legal_instruments` code to reflect new project structure
- Removed unused dependencies
- Removed deprecated data files (Have been moved to other repo)
- Added Courier module
- Added Courier data 


# TODO
- Extract "as is"

- Från index ta ut rubriker (och sidnummer)
	article_index.loc[article_index["courier_id"] == "012656"]["catalogue_title"]

- För varje rubrik: Hitta alla sidnummer rubriker förekommer i i XML:er

Test: Hitta alla artiklar
Antagande: Stora bokstäver