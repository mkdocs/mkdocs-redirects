import pytest

from mkdocs_redirects.plugin import get_relative_html_path


@pytest.mark.parametrize(["old_page", "new_page", "expected"], [
    ("old.md", "index.md", "../"),
    ("old.md", "README.md", "../"),
    ("old.md", "new.md", "../new/"),
    ("old.md", "new/index.md", "../new/"),
    ("old.md", "new/README.md", "../new/"),
    ("foo/old.md", "foo/new.md", "../new/"),
    ("foo/fizz/old.md", "foo/bar/new.md", "../../bar/new/"),
    ("fizz/old.md", "foo/bar/new.md", "../../foo/bar/new/"),
])
def test_relative_redirect_directory_urls(old_page, new_page, expected):
    result = get_relative_html_path(old_page, new_page, use_directory_urls=True)

    assert result == expected


@pytest.mark.parametrize(["old_page", "new_page", "expected"], [
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
])
def test_relative_redirect_no_directory_urls(old_page, new_page, expected):
    result = get_relative_html_path(old_page, new_page, use_directory_urls=False)

    assert result == expected
