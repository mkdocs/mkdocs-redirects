#!/bin/sh
set -e

cd "$(dirname "$0")/.."

with_groups() {
    echo "::group::$@"
    "$@" && echo "::endgroup::"
}

srcs='mkdocs_redirects tests setup.py'

"$@" pytest -q
"$@" autoflake -i -r --remove-all-unused-imports --remove-unused-variables $srcs
"$@" isort -q $srcs
"$@" black -l100 -tpy36 --skip-string-normalization -q $srcs
