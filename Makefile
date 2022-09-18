clean:  ## Clean intermediate build files
	find . -name '__pycache__' | xargs rm -rf
	find . -name '*.pyc' | xargs rm -rf
	rm -rf dist/
.PHONY: clean

build: clean dev  ## Build the package (source distribution)
	python setup.py sdist
.PHONY: build

dev: clean  ## Setup development environment
	pip install .[dev]
.PHONY: dev

test: dev ## Run tests
	.tools/ci.sh
.PHONY: test

release: build  ## Release to PyPi
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
.PHONY: release
