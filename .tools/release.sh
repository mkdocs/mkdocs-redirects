#!/bin/bash

set -e -u -x
cd "$(dirname "$0")/.."

git diff --staged --quiet
git diff --quiet HEAD pyproject.toml
rm -rf dist
hatch version "$1"
hatch build
git add */__init__.py
git commit -m "v$1"
git tag -a -m "" "v$1"
git push origin master --tags
