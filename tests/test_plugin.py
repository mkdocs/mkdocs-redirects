"""
Copyright 2019-2022 DataRobot, Inc. and its affiliates.
All rights reserved.
"""
import pytest

from mkdocs_redirects.plugin import get_relative_html_path, _split_hash_fragment
from mkdocs.structure.files import File


@pytest.mark.parametrize(
    ["old_page", "new_page", "expected"],
    [
        ("old.md", "index.md", "../"),
        ("old.md", "README.md", "../"),
        ("old.md", "new.md", "../new/"),
        ("old.md", "new/index.md", "../new/"),
        ("old.md", "new/README.md", "../new/"),
        ("foo/old.md", "foo/new.md", "../new/"),
        ("foo/fizz/old.md", "foo/bar/new.md", "../../bar/new/"),
        ("fizz/old.md", "foo/bar/new.md", "../../foo/bar/new/"),
        ("old.md", "index.md#hash", "../#hash"),
        ("old.md", "README.md#hash", "../#hash"),
        ("old.md", "new.md#hash", "../new/#hash"),
        ("old.md", "new/index.md#hash", "../new/#hash"),
        ("old.md", "new/README.md#hash", "../new/#hash"),
        ("foo/old.md", "foo/new.md#hash", "../new/#hash"),
        ("foo/fizz/old.md", "foo/bar/new.md#hash", "../../bar/new/#hash"),
        ("fizz/old.md", "foo/bar/new.md#hash", "../../foo/bar/new/#hash"),
    ],
)
def test_relative_redirect_directory_urls(old_page, new_page, expected):
    page_new_without_hash, hash = _split_hash_fragment(new_page)
    file = File(page_new_without_hash, "docs", "site", True)
    result = get_relative_html_path(old_page, file.url + hash, use_directory_urls=True)

    assert result == expected


@pytest.mark.parametrize(
    ["old_page", "new_page", "expected"],
    [
        ("old.md", "index.md", "index.html"),
        ("old.md", "README.md", "index.html"),
        ("old.md", "new.md", "new.html"),
        ("old.md", "new/index.md", "new/index.html"),
        ("old.md", "new/README.md", "new/index.html"),
        ("foo/old.md", "foo/new.md", "new.html"),
        ("foo/fizz/old.md", "foo/bar/new.md", "../bar/new.html"),
        ("fizz/old.md", "foo/bar/new.md", "../foo/bar/new.html"),
        ("foo.md", "foo/index.md", "foo/index.html"),
        ("foo.md", "foo/README.md", "foo/index.html"),
        ("old.md", "index.md#hash", "index.html#hash"),
        ("old.md", "README.md#hash", "index.html#hash"),
        ("old.md", "new.md#hash", "new.html#hash"),
        ("old.md", "new/index.md#hash", "new/index.html#hash"),
        ("old.md", "new/README.md#hash", "new/index.html#hash"),
        ("foo/old.md", "foo/new.md#hash", "new.html#hash"),
        ("foo/fizz/old.md", "foo/bar/new.md#hash", "../bar/new.html#hash"),
        ("fizz/old.md", "foo/bar/new.md#hash", "../foo/bar/new.html#hash"),
        ("foo.md", "foo/index.md#hash", "foo/index.html#hash"),
        ("foo.md", "foo/README.md#hash", "foo/index.html#hash"),
    ],
)
def test_relative_redirect_no_directory_urls(old_page, new_page, expected):
    page_new_without_hash, hash = _split_hash_fragment(new_page)
    file = File(page_new_without_hash, ".", ".", False)
    result = get_relative_html_path(old_page, "".join([file.url, hash]), use_directory_urls=False)

    assert result == expected
