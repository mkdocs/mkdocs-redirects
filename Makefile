release:
	rm -rf dist
	pip install .[release]
	python setup.py sdist
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
.PHONY: release
