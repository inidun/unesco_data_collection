SHELL := /bin/bash
SOURCE_FOLDERS=courier tests tmp
PACKAGE_FOLDER=courier
BLACK_ARGS=--line-length 120 --target-version py38 --skip-string-normalization -q
FLAKE8_ARGS=--extend-ignore=BLK100,E302,E303
MYPY_ARGS=--show-column-numbers --no-error-summary
ISORT_ARGS=--profile black --float-to-top --line-length 120 --py 38
#PYTEST_ARGS=--durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html tests
PYTEST_ARGS=--cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html

tidy: isort black

lint: tidy pylint flake8 mypy

clean:
	@rm -rf .coverage coverage.xml htmlcov
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@rm -rf tests/output

test: clean
	@mkdir -p ./tests/output
	@poetry run pytest $(PYTEST_ARGS) tests
	@rm -rf ./tests/output/*

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

# tools:
# 	@pip install --upgrade pip -q
# 	@pip install poetry --upgrade -q
# 	@poetry run pip install --upgrade pip -q

# NOTE: tools should not be run while in poetry shell
# .PHONY: tools

.PHONY: help
.PHONY: clean
.PHONY: test
.PHONY: lint pylint flake8 mypy pylint_diff
.PHONY: tidy black isort

help:
	@echo "Higher level recepies: "
	@echo " make clean            Removes temporary files, caches, and build files"
	@echo " make lint             Runs tidy, pylint, flake8 and mypy"
	@echo " make test             Runs tests with code coverage"
	@echo " make tidy             Runs black and isort"
	@echo "  "
	@echo "Lower level recepies: "
	@echo " make black            Runs black"
	@echo " make flake8           Runs flake8"
	@echo " make isort            Runs isort"
	@echo " make mypy             Runs mypy"
	@echo " make pylint           Runs pylint"
	@echo " make pylint_diff      Runs pylint on changed files only"