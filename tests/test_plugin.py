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
    "100%.md",
    "the/fake.md",
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
    plg.doc_pages["the/fake.md"].dest_path = "fake/destination/index.html"
    plg.doc_pages["the/fake.md"].url = plg.doc_pages["the/fake.md"]._get_url(use_directory_urls)

    plg.on_post_build(dict(use_directory_urls=use_directory_urls, site_dir="site"))

    return wrote


@pytest.fixture
def actual_redirect_target(run_redirect_test):
    assert bool(run_redirect_test)
    return run_redirect_test[1]


@pytest.fixture
def actual_written_file(run_redirect_test):
    assert bool(run_redirect_test)
    return run_redirect_test[0]


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
    ("foo.md", "the/fake.md", "fake/destination/index.html", "../fake/destination/"),
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
    ("foo.md", "the/fake.md#hash", "fake/destination/index.html#hash", "../fake/destination/#hash"),
    ("foo.md", "100%.md", "100%25.html", "../100%25/"),
    ("foo/fizz/old.md",) + ("https://example.org/old.md",) * 3,
]


@pytest.mark.parametrize("use_directory_urls", [False])
@pytest.mark.parametrize(["old_page", "new_page", "expected", "_"], testdata)
def test_relative_redirect_no_directory_urls(actual_redirect_target, expected, _):
    assert actual_redirect_target == expected


@pytest.mark.parametrize("use_directory_urls", [True])
@pytest.mark.parametrize(["old_page", "new_page", "_", "expected"], testdata)
def test_relative_redirect_directory_urls(actual_redirect_target, _, expected):
    assert actual_redirect_target == expected


# Tuples of:
# * Left side of the redirect item
# * Expected path of the written HTML file, use_directory_urls=False
# * Expected path of the written HTML file, use_directory_urls=True
testdata = [
    ("old.md", "old.html", "old/index.html"),
    ("README.md", "index.html", "index.html"),
    ("100%.md", "100%.html", "100%/index.html"),
    ("foo/fizz/old.md", "foo/fizz/old.html", "foo/fizz/old/index.html"),
    ("foo/fizz/index.md", "foo/fizz/index.html", "foo/fizz/index.html"),
]


@pytest.mark.parametrize("use_directory_urls", [False])
@pytest.mark.parametrize("new_page", ["new.md"])
@pytest.mark.parametrize(["old_page", "expected", "_"], testdata)
def test_page_dest_path_no_directory_urls(actual_written_file, old_page, expected, _):
    assert actual_written_file == expected


@pytest.mark.parametrize("use_directory_urls", [True])
@pytest.mark.parametrize("new_page", ["new.md"])
@pytest.mark.parametrize(["old_page", "_", "expected"], testdata)
def test_page_dest_path_directory_urls(actual_written_file, old_page, _, expected):
    assert actual_written_file == expected
