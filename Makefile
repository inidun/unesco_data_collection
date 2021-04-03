SHELL := /bin/bash
SOURCE_FOLDERS=courier tests tmp
PACKAGE_FOLDER=courier
PYTEST_ARGS=--durations=0 --cov=$(PACKAGE_FOLDER) --cov-report=xml --cov-report=html tests
BLACK_ARGS=--line-length 120 --target-version py38 --skip-string-normalization
ISORT_ARGS=--profile black --float-to-top --line-length 120 --py 38

lint: tidy pylint flake8

tidy: isort black

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
	@poetry run pylint --version
	@time poetry run pylint $(SOURCE_FOLDERS)

flake8:
	@poetry run flake8 --version
	@poetry run flake8 $(SOURCE_FOLDERS)

black: clean
	@poetry run black --version
	@poetry run black $(BLACK_ARGS) $(SOURCE_FOLDERS)

isort:
	@poetry run isort $(ISORT_ARGS) $(SOURCE_FOLDERS)

tools:
	@pip install --upgrade pip -q
	@pip install poetry --upgrade -q
	@poetry run pip install --upgrade pip -q

outated:
	@poetry show -o

update:
	@poetry update

.PHONY: help
.PHONY: clean
.PHONY: test
.PHONY: pylint flake8 lint
.PHONY: black isort tidy
.PHONY: outated update

# NOTE: tools should not be run while in poetry shell
# .PHONY: tools

help:
	@echo "Higher level recepies: "
	@echo " make clean            Removes temporary files, caches, build files"
	@echo " make test             Runs tests with code coverage"
	@echo " make tidy             Runs black and isort"
	@echo "  "
	@echo "Lower level recepies: "
	@echo " make outated          Show outdated dependencies"
	@echo " make update           Updates dependencies"
	@echo " make yapf             Runs yapf"
	@echo " make isort            Runs isort"