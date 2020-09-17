# Configuration
APP_ROOT := $(abspath $(lastword $(MAKEFILE_LIST))/..)
APP_NAME := sandpiper
VENV?=/tmp/sandpiper-venv
PYTHON=${VENV}/bin/python3
PIP=${VENV}/bin/pip

WPS_URL = http://localhost:5003

export PIP_INDEX_URL=https://pypi.pacificclimate.org/simple

# Used in target refresh-notebooks to make it looks like the notebooks have
# been refreshed from the production server below instead of from the local dev
# instance so the notebooks can also be used as tutorial notebooks.
OUTPUT_URL = https://docker-dev03.pcic.uvic.ca/wpsoutputs

.PHONY: all
all: apt develop test-all clean-test

.PHONY: help
help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "  help              to print this help message. (Default)"
	@echo "  install           to install app by running 'pip install -e .'"
	@echo "  develop           to install with additional development requirements."
	@echo "  start             to start $(APP_NAME) service as daemon (background process)."
	@echo "  stop              to stop $(APP_NAME) service."
	@echo "  restart           to restart $(APP_NAME) service."
	@echo "  status            to show status of $(APP_NAME) service."
	@echo "  clean             to remove all files generated by build and tests."
	@echo "\nTesting targets:"
	@echo "  test              to run tests (but skip long running tests)."
	@echo "  test-all          to run all tests (including long running tests)."
	@echo "  lint              to run code style checks with flake8."
	@echo "\nSphinx targets:"
	@echo "  docs              to generate HTML documentation with Sphinx."
	@echo "\nDeployment targets:"
	@echo "  dist              to build source and wheel package."

## Build targets

.PHONY: apt
apt:
	@echo "Installing gdal ..."
	@-bash -c "sudo apt-get install -y gdal-bin libgdal-dev"

.PHONY: install
install: venv
	@echo "Installing application ..."
	@-bash -c '${PIP} install .'
	@echo "\nStart service with \`sandpiper start'"

.PHONY: develop
develop: venv
	@echo "Installing development requirements for tests and docs ..."
	@-bash -c '${PIP} install -e ".[dev]"'

.PHONY: start
start: venv
	@echo "Starting application ..."
	@-bash -c "${VENV}/bin/$(APP_NAME) start -d"

.PHONY: stop
stop: venv
	@echo "Stopping application ..."
	@-bash -c "${VENV}/bin/$(APP_NAME) stop"

.PHONY: restart
restart: venv stop start
	@echo "Restarting application ..."

.PHONY: status
status: venv
	@echo "Show status ..."
	@-bash -c "${VENV}/bin/$(APP_NAME) status"

.PHONY: clean
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build:
	@echo "Remove build artifacts ..."
	@-rm -fr build/
	@-rm -fr dist/
	@-rm -fr .eggs/
	@-find . -name '*.egg-info' -exec rm -fr {} +
	@-find . -name '*.egg' -exec rm -f {} +
	@-find . -name '*.log' -exec rm -fr {} +
	@-find . -name '*.sqlite' -exec rm -fr {} +

.PHONY: clean-pyc
clean-pyc:
	@echo "Remove Python file artifacts ..."
	@-find . -name '*.pyc' -exec rm -f {} +
	@-find . -name '*.pyo' -exec rm -f {} +
	@-find . -name '*~' -exec rm -f {} +
	@-find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test:
	@echo "Remove test artifacts ..."
	@-rm -fr .pytest_cache

.PHONY: clean-dist
clean-dist: clean
	@echo "Running 'git clean' ..."
	@git diff --quiet HEAD || echo "There are uncommitted changes! Aborting 'git clean' ..."
	## do not use git clean -e/--exclude here, add them to .gitignore instead
	@-git clean -dfx

.PHONY: venv
venv:
	test -d $(VENV) || python3 -m venv $(VENV)

## Test targets

.PHONY: test
test: venv
	@echo "Running tests (skip slow and online tests) ..."
	@bash -c '${PYTHON} -m pytest -v -m "not slow and not online" tests/'

.PHONY: test-all
test-all: venv
	@echo "Running all tests (including slow and online tests) ..."
	@bash -c '${PYTHON} -m pytest -v tests/'

.PHONY: notebook-sanitizer
notebook-sanitizer:
	@echo "Copying notebook output sanitizer ..."
	@-bash -c "curl -L $(SANITIZE_FILE) -o $(CURDIR)/docs/source/output-sanitize.cfg --silent"

.PHONY: test-notebooks
test-notebooks: notebook-sanitizer
	@echo "Running notebook-based tests"
	@bash -c "source $(VENV)/bin/activate"
	@bash -c "env WPS_URL=$(WPS_URL) pytest --nbval --verbose $(CURDIR)/docs/source/notebooks/ --sanitize-with $(CURDIR)/docs/source/output-sanitize.cfg --ignore $(CURDIR)/docs/source/notebooks/.ipynb_checkpoints"

.PHONY: lint
lint: venv
	@echo "Running black code style checks ..."
	@bash -c '${PYTHON} -m black . --check'

.PHONY: refresh-notebooks
refresh-notebooks:
	@echo "Refresh all notebook outputs under docs/source/notebooks"
	@bash -c 'for nb in $(CURDIR)/docs/source/notebooks/*.ipynb; do WPS_URL="$(WPS_URL)" jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=60 --output "$$nb" "$$nb"; sed -i "s@$(WPS_URL)/outputs/@$(OUTPUT_URL)/@g" "$$nb"; done; cd $(APP_ROOT)'

## Sphinx targets

.PHONY: docs
docs:
	@echo "Generating docs with Sphinx ..."
	@bash -c '$(MAKE) -C $@ clean html'
	@echo "Open your browser to: file:/$(APP_ROOT)/docs/build/html/index.html"
	## do not execute xdg-open automatically since it hangs travis and job does not complete
	@echo "xdg-open $(APP_ROOT)/docs/build/html/index.html"

## Deployment targets

.PHONY: dist
dist: clean
	@echo "Building source and wheel package ..."
	@-python setup.py sdist
	@-python setup.py bdist_wheel
	@-bash -c 'ls -l dist/'
