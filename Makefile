SHELL := /bin/bash
SOURCE_FOLDERS=courier tests
PACKAGE_FOLDER=courier
BLACK_ARGS=--line-length 120 --target-version py310 --skip-string-normalization -q
FLAKE8_ARGS=--extend-ignore=BLK100,E302,E303
MYPY_ARGS=--show-column-numbers --no-error-summary --python-version 3.10
ISORT_ARGS=--profile black --float-to-top --line-length 120 --py 310

tidy: isort black
.PHONY: tidy

lint: tidy pylint flake8
.PHONY: lint

typing: lint mypy
.PHONY: typing

clean:
	@rm -rf .coverage coverage.xml htmlcov .nox
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@rm -rf tests/output
.PHONY: clean

output-dir:
	@mkdir -p ./tests/output

test: output-dir
	@poetry run pytest -m "not slow" --durations=0 tests/
	@rm -rf ./tests/output/*

coverage: output-dir
	@poetry run pytest -m "not slow" --durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html --cov-branch tests/
	@rm -rf ./tests/output/*
.PHONY: coverage

test-courier: output-dir
	@poetry run pytest --durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html --cov-branch tests/$(PACKAGE_FOLDER)
	@rm -rf ./tests/output/*
.PHONY: test-courier

test-no-java: output-dir
	@poetry run pytest -m "not java" --durations=0 tests/$(PACKAGE_FOLDER)
	@rm -rf ./tests/output/*
.PHONY: test-no-java

test-java: output-dir
	# @poetry run pytest -m "java" -p no:faulthandler tests/$(PACKAGE_FOLDER)
	@poetry run pytest -m "java" tests/$(PACKAGE_FOLDER)
	@rm -rf ./tests/output/*
.PHONY: test-java

test-slow: output-dir
	@poetry run pytest -m "slow" --durations=0 tests
	@rm -rf ./tests/output/*
.PHONY: test-slow

test-all: output-dir
	@poetry run pytest --durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html --cov-branch tests/
	@rm -rf ./tests/output/*
.PHONY: test-all

retest: output-dir
	@poetry run pytest --durations=0 --last-failed tests
.PHONY: retest


pylint:
	@poetry run pylint --version | grep pylint
	@poetry run pylint $(SOURCE_FOLDERS)
.PHONY: pylint

.ONESHELL: pylint_diff
pylint_diff:
	@delta_files=$$(git status --porcelain | awk '{print $$2}' | grep -E '\.py$$' | tr '\n' ' ')
	@if [[ "$$delta_files" != "" ]]; then
		poetry run pylint --version | grep pylint
		poetry run pylint $$delta_files
	fi
.PHONY: pylint_diff

notes:
	@poetry run pylint --version | grep pylint
	@poetry run pylint --notes=FIXME,XXX,TODO --disable=all --enable=W0511 -f colorized $(SOURCE_FOLDERS)
.PHONY: notes

flake8:
	@poetry run flake8 --version
	@poetry run flake8 $(FLAKE8_ARGS) $(SOURCE_FOLDERS)
.PHONY: flake8

mypy:
	@poetry run mypy --version
	@poetry run mypy $(MYPY_ARGS) $(SOURCE_FOLDERS)
.PHONY: mypy

black:
	@poetry run black --version
	@poetry run black $(BLACK_ARGS) $(SOURCE_FOLDERS)
.PHONY: black

isort:
	@echo isort `poetry run isort --vn`
	@poetry run isort $(ISORT_ARGS) $(SOURCE_FOLDERS)
.PHONY: isort

REPORTDIR = ./report

report-dir:
	@mkdir -p $(REPORTDIR)

corpus_report: report-dir
	@export PYTHONPATH=.
	@poetry run python courier/scripts/corpus_report.py $(REPORTDIR)
.PHONY: corpus_report

lib-dir:
	@mkdir -p courier/lib

download_pdfextract: lib-dir
	@wget -q -O courier/lib/pdfextract-1.0-SNAPSHOT.jar https://github.com/inidun/pdfextract/releases/download/1.0-SNAPSHOT/pdfextract-1.0-SNAPSHOT.jar

setup: download_pdfextract
.PHONY: setup

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
.PHONY: help
