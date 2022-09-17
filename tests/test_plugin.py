"""
Copyright 2019-2022 DataRobot, Inc. and its affiliates.
All rights reserved.
"""
import pytest
from mkdocs.structure.files import File

from mkdocs_redirects import plugin

existing_pages = [
    "README.md",
    "foo/README.md",
    "foo/bar/new.md",
    "foo/index.md",
    "foo/new.md",
    "index.md",
    "new.md",
    "new/README.md",
    "new/index.md",
]


@pytest.fixture
def run_redirect_test(monkeypatch, old_page, new_page, use_directory_urls):
    wrote = ()

    def write_html(site_dir, old_path, new_path):
        nonlocal wrote
        wrote = (old_path, new_path)

    monkeypatch.setattr(plugin, "write_html", write_html)

    plg = plugin.RedirectPlugin()
    plg.redirects = {old_page: new_page}
    plg.doc_pages = {
        path: File(path, "docs", "site", use_directory_urls) for path in existing_pages
    }

    plg.on_post_build(dict(use_directory_urls=use_directory_urls, site_dir="site"))

    return wrote


@pytest.fixture
def actual_redirect_target(run_redirect_test):
    assert bool(run_redirect_test)
    return run_redirect_test[1]


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


@pytest.mark.parametrize("use_directory_urls", [False])
@pytest.mark.parametrize(["old_page", "new_page", "expected", "_"], testdata)
def test_relative_redirect_no_directory_urls(actual_redirect_target, expected, _):
    assert actual_redirect_target == expected


@pytest.mark.parametrize("use_directory_urls", [True])
@pytest.mark.parametrize(["old_page", "new_page", "_", "expected"], testdata)
def test_relative_redirect_directory_urls(actual_redirect_target, _, expected):
    assert actual_redirect_target == expected
