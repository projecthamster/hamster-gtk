BUILDDIR = _build

.PHONY: clean-pyc clean-build docs clean

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "   clean         to remove all build, test, coverage and Python artifacts"
	@echo "   clean-build   to remove build artifacts"
	@echo "   clean-pyc     to remove Python file artifacts"
	@echo "   clean-docs"
	@echo "   clean-test    to remove test and coverage artifacts"
	@echo "   lint          to check style with flake8"
	@echo "   test          to run tests quickly with the default Python"
	@echo "   test-all      to run tests on every Python version with tox"
	@echo "   coverage      to check code coverage quickly with the default Python"
	@echo "   coverage-html"
	@echo "   codecov"
	@echo "   develop       to install (or update) all packages required for development"
	@echo "   docs          to generate Sphinx HTML documentation, including API docs"
	@echo "   isort         to run isort on the whole project."
	@echo "   release       to package and upload a release"
	@echo "   dist          to package"
	@echo "   install       to install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-docs:
	$(MAKE) -C docs clean BUILDDIR=$(BUILDDIR)

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

develop:
	pip install -U pip setuptools wheel
	pip install -U -e .
	pip install -U -r requirements/dev.pip

lint:
	flake8 hamster-dbus tests

test:
	py.test $(TEST_ARGS) tests/

test-all:
	tox

coverage:
	coverage run -m pytest $(TEST_ARGS) tests
	coverage report

test2:
	py.test tests

coverage-html: coverage
	coverage html
	$(BROWSER) htmlcov/index.html

codecov: coverage
	codecov --token=96b66aeb-8d82-4d44-8ff7-93ac5d5305b9

docs:
	rm -f docs/hamster_gtk.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ hamster_gtk
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

isort:
	isort --recursive setup.py hamster_gtk/ tests/


servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: clean
	python setup.py sdist bdist_wheel
	twine upload -r pypi -s dist/*

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean
	python setup.py install
