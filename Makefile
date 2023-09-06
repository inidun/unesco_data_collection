SHELL := /bin/bash
SOURCE_FOLDERS=courier tests
PACKAGE_FOLDER=courier
BLACK_ARGS=--line-length 120 --target-version py310 --skip-string-normalization -q
FLAKE8_ARGS=--extend-ignore=BLK100,E302,E303
MYPY_ARGS=--show-column-numbers --no-error-summary --python-version 3.10
ISORT_ARGS=--profile black --float-to-top --line-length 120 --py 310

tidy: isort black

lint: tidy pylint flake8

typing: lint mypy

clean:
	@rm -rf .coverage coverage.xml htmlcov .nox
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@rm -rf tests/output

test: output-dir
	@poetry run pytest -m "not slow" --durations=0 tests/
	@rm -rf ./tests/output/*

coverage: output-dir
	@poetry run pytest -m "not slow" --durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html --cov-branch tests/
	@rm -rf ./tests/output/*

test-courier: output-dir
	@poetry run pytest --durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html --cov-branch tests/$(PACKAGE_FOLDER)
	@rm -rf ./tests/output/*

test-no-java: output-dir
	@poetry run pytest -m "not java" --durations=0 tests/$(PACKAGE_FOLDER)
	@rm -rf ./tests/output/*

test-java: output-dir
	# @poetry run pytest -m "java" -p no:faulthandler tests/$(PACKAGE_FOLDER)
	@poetry run pytest -m "java" tests/$(PACKAGE_FOLDER)
	@rm -rf ./tests/output/*

test-slow: output-dir
	@poetry run pytest -m "slow" --durations=0 tests
	@rm -rf ./tests/output/*

test-all: output-dir
	@poetry run pytest --durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html --cov-branch tests/
	@rm -rf ./tests/output/*

retest: output-dir
	@poetry run pytest --durations=0 --last-failed tests

output-dir:
	@mkdir -p ./tests/output

.PHONY: retest coverage test-courier test-no-java test-java test-slow test-all typing

pylint:
	@poetry run pylint --version | grep pylint
	@poetry run pylint $(SOURCE_FOLDERS)

.ONESHELL: pylint_diff
pylint_diff:
	@delta_files=$$(git status --porcelain | awk '{print $$2}' | grep -E '\.py$$' | tr '\n' ' ')
	@if [[ "$$delta_files" != "" ]]; then
		poetry run pylint --version | grep pylint
		poetry run pylint $$delta_files
	fi

notes:
	@poetry run pylint --version | grep pylint
	@poetry run pylint --notes=FIXME,XXX,TODO --disable=all --enable=W0511 -f colorized $(SOURCE_FOLDERS)

flake8:
	@poetry run flake8 --version
	@poetry run flake8 $(FLAKE8_ARGS) $(SOURCE_FOLDERS)

mypy:
	@poetry run mypy --version
	@poetry run mypy $(MYPY_ARGS) $(SOURCE_FOLDERS)

black:
	@poetry run black --version
	@poetry run black $(BLACK_ARGS) $(SOURCE_FOLDERS)

isort:
	@echo isort `poetry run isort --vn`
	@poetry run isort $(ISORT_ARGS) $(SOURCE_FOLDERS)

PDFS = ~/data/courier/pdf
PAGES = ~/data/courier/pages
XML = ~/data/courier/xml
REPORT = ~/data/courier/report

report-dir:
	@mkdir -p $(REPORT)

corpus_report: report-dir
	@export PYTHONPATH=.
	@poetry run python courier/scripts/corpus_report.py $(REPORT)

lib-dir:
	@mkdir -p courier/lib

download_pdfextract: lib-dir
	@wget -q -O courier/lib/pdfextract-1.0-SNAPSHOT.jar https://github.com/inidun/pdfextract/releases/download/1.0-SNAPSHOT/pdfextract-1.0-SNAPSHOT.jar

setup: download_pdfextract

.PHONY: setup

.PHONY: corpus_report

.PHONY: help
.PHONY: clean
.PHONY: test
.PHONY: lint pylint flake8 mypy pylint_diff notes
.PHONY: tidy black isort

help:
	@echo "Higher level recepies: "
	@echo " make clean            Removes temporary files, caches, and build files"
	@echo " make lint             Runs tidy, pylint, flake8 and mypy"
	@echo " make typing           Runs lint and mypy"
	@echo " make test             Runs tests"
	@echo " make coverage         Runs tests with code coverage"
	@echo " make tidy             Runs black and isort"
	@echo " make setup            Setup environment"
	@echo "  "
	@echo "Lower level recepies: "
	@echo " make black            Runs black"
	@echo " make flake8           Runs flake8"
	@echo " make isort            Runs isort"
	@echo " make mypy             Runs mypy"
	@echo " make notes            Runs pylint with notes"
	@echo " make pylint           Runs pylint"
	@echo " make pylint_diff      Runs pylint on changed files only"
	@echo "  "
	@echo " make corpus_report    Generate corpus report"
