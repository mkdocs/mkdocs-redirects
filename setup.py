"""Installation using setup.py is not supported.
Use `pip install .` instead."""

import sys

from setuptools import setup

sys.exit(__doc__)

# Fake reference so GitHub still considers it a real package for statistics purposes.
setup(
    name="mkdocs-redirects",
)
