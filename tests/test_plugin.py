"""
Copyright 2019-2022 DataRobot, Inc. and its affiliates.
All rights reserved.
"""
import pytest
from mkdocs.structure.files import File

from mkdocs_redirects.plugin import _split_hash_fragment, get_relative_html_path

# Tuples of:
# * Left side of the redirect item
# * Right side of the redirect item
# * Expected destination URL written into the HTML file, use_directory_urls=False
# * Expected destination URL written into the HTML file, use_directory_urls=True
testdata = [
    ("old.md", "index.md", "index.html", "../"),
    ("old.md", "README.md", "index.html", "../"),
    ("old.md", "new.md", "new.html", "../new/"),
    ("old.md", "new/index.md", "new/index.html", "../new/"),
    ("old.md", "new/README.md", "new/index.html", "../new/"),
    ("foo/old.md", "foo/new.md", "new.html", "../new/"),
    ("foo/fizz/old.md", "foo/bar/new.md", "../bar/new.html", "../../bar/new/"),
    ("fizz/old.md", "foo/bar/new.md", "../foo/bar/new.html", "../../foo/bar/new/"),
    ("foo.md", "foo/index.md", "foo/index.html", "./"),
    ("foo.md", "foo/README.md", "foo/index.html", "./"),
    ("old.md", "index.md#hash", "index.html#hash", "../#hash"),
    ("old.md", "README.md#hash", "index.html#hash", "../#hash"),
    ("old.md", "new.md#hash", "new.html#hash", "../new/#hash"),
    ("old.md", "new/index.md#hash", "new/index.html#hash", "../new/#hash"),
    ("old.md", "new/README.md#hash", "new/index.html#hash", "../new/#hash"),
    ("foo/old.md", "foo/new.md#hash", "new.html#hash", "../new/#hash"),
    ("foo/fizz/old.md", "foo/bar/new.md#hash", "../bar/new.html#hash", "../../bar/new/#hash"),
    ("fizz/old.md", "foo/bar/new.md#hash", "../foo/bar/new.html#hash", "../../foo/bar/new/#hash"),
    ("foo.md", "foo/index.md#hash", "foo/index.html#hash", "./#hash"),
    ("foo.md", "foo/README.md#hash", "foo/index.html#hash", "./#hash"),
]


@pytest.mark.parametrize(["old_page", "new_page", "_", "expected"], testdata)
def test_relative_redirect_directory_urls(old_page, new_page, _, expected):
    page_new_without_hash, hash = _split_hash_fragment(new_page)
    file = File(page_new_without_hash, "docs", "site", True)
    result = get_relative_html_path(old_page, file.url + hash, use_directory_urls=True)

    assert result == expected


@pytest.mark.parametrize(["old_page", "new_page", "expected", "_"], testdata)
def test_relative_redirect_no_directory_urls(old_page, new_page, expected, _):
    page_new_without_hash, hash = _split_hash_fragment(new_page)
    file = File(page_new_without_hash, "docs", "site", False)
    result = get_relative_html_path(old_page, file.url + hash, use_directory_urls=False)

    assert result == expected
