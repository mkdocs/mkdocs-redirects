"""
Copyright 2019-2022 DataRobot, Inc. and its affiliates.
All rights reserved.
"""
from __future__ import annotations

import os
import posixpath
from typing import TypedDict

from mkdocs import utils
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import File

log = get_plugin_logger(__name__)


def gen_anchor_redirects(anchor_list: list):
    """
    Generate a dictionary of redirects for anchors.

    :param anchor_list: A list of tuples containing old anchors and new links.
    :return: A string of JavaScript redirects for the anchors.
    """
    js_redirects = ""
    for old_anchor, new_link in anchor_list:
        # Create a JavaScript redirect for each anchor
        js_redirects += f"""
        if (window.location.hash === "{old_anchor}") {{
            location.href = "{new_link}";
        }}
        """
    return js_redirects


# This template is used to generate the HTML file for the redirect.
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <link rel="canonical" href="{url}">
    <script>
        var anchor = window.location.hash.substr(1);
        location.href = `{url}${{anchor ? '#' + anchor : ''}}`;
        {redirects}
    </script>
    <meta http-equiv="refresh" content="0; url={url}">
</head>
<body>
You're being redirected to a <a href="{url}">new destination</a>.
</body>
</html>
"""

JS_INJECT_EXISTS = """
<script>
    {redirects}
</script>
"""


def write_html(site_dir: str, old_path: str, new_path: str, anchor_list: list[tuple[str, str]]) -> None:
    """Write an HTML file in the site_dir with a meta redirect to the new page"""
    # Determine all relevant paths
    old_path_abs = os.path.join(site_dir, old_path)
    old_dir = os.path.dirname(old_path)
    old_dir_abs = os.path.dirname(old_path_abs)

    # Create parent directories if they don't exist
    if not os.path.exists(old_dir_abs):
        log.debug("Creating directory '%s'", old_dir)
        os.makedirs(old_dir_abs)

    # Write the HTML redirect file in place of the old file
    log.debug("Creating redirect: '%s' -> '%s'", old_path, new_path)
    redirects = gen_anchor_redirects(anchor_list)  # Example anchor map
    content = HTML_TEMPLATE.format(url=new_path, redirects=redirects)
    with open(old_path_abs, "w", encoding="utf-8") as f:
        f.write(content)


def get_relative_html_path(old_page, new_page, use_directory_urls):
    """Return the relative path from the old html path to the new html path"""
    old_path = get_html_path(old_page, use_directory_urls)
    new_path, new_hash_fragment = _split_hash_fragment(new_page)

    relative_path = posixpath.relpath(new_path, start=posixpath.dirname(old_path))
    if use_directory_urls:
        relative_path = relative_path + "/"

    return relative_path + new_hash_fragment


def get_html_path(path, use_directory_urls):
    """Return the HTML file path for a given markdown file"""
    f = File(path, "", "", use_directory_urls)
    return f.dest_path.replace(os.sep, "/")


class RedirectEntry(TypedDict):
    hashes: list[tuple[str, str]]
    overall: str


def build_redirect_entries(redirects: dict) -> dict[str, RedirectEntry]:
    """
    This builds a more-detailed lookup table from the original old->new page mappings.

    For each old page, it contains an overall redirect of where to go,
    as well as specific redirects for each hash, contained in a (hash, redirect) structure.
    """
    redirect_entries: dict[str, RedirectEntry] = {}
    for page_old, page_new in redirects.items():
        page_old_without_hash, old_hash = _split_hash_fragment(str(page_old))
        if page_old_without_hash not in redirect_entries:
            redirect_entries[page_old_without_hash] = {"hashes": [], "overall": ""}
        if old_hash == "":
            redirect_entries[page_old_without_hash]["overall"] = page_new
        else:
            redirect_entries[page_old_without_hash]["hashes"].append((old_hash, page_new))

    # If a page doesn't have an overall redirect, use the first hash redirect
    for page_old, redirect_map in redirect_entries.items():
        if redirect_map.get("overall", "") == "":
            redirect_entries[page_old]["overall"] = redirect_map["hashes"][0][1]

    return redirect_entries


class RedirectPlugin(BasePlugin):
    # Any options that this plugin supplies should go here.
    config_scheme = (
        ("redirect_maps", config_options.Type(dict, default={})),  # note the trailing comma
    )

    redirect_entries: dict[str, RedirectEntry]

    # Build a list of redirects on file generation
    def on_files(self, files, config, **kwargs):
        self.redirects = self.config.get("redirect_maps", {})

        # Validate user-provided redirect "old files"
        for page_old in self.redirects:
            page_old_without_hash, _ = _split_hash_fragment(str(page_old))
            if not utils.is_markdown_file(page_old_without_hash):
                log.warning(
                    "redirects plugin: '%s' is not a valid markdown file!", page_old_without_hash
                )

        # Build a dict of known document pages to validate against later
        self.doc_pages = {}
        for page in files.documentation_pages():  # object type: mkdocs.structure.files.File
            self.doc_pages[page.src_path.replace(os.sep, "/")] = page

        # Create a dictionary to hold anchor maps for redirects
        self.redirect_entries = build_redirect_entries(self.redirects)

    def on_page_content(self, html, page, config, files):
        use_directory_urls = config.get("use_directory_urls")
        page_old = page.file.src_uri
        if page_old not in self.redirect_entries:
            return html

        hash_redirects = self.redirect_entries[page_old]["hashes"]
        for i in range(len(hash_redirects)):
            old_hash, new_link = hash_redirects[i]
            hash_redirect_without_hash, new_hash = _split_hash_fragment(str(new_link))
            # If we are redirecting to a page that exists, update the destination hash path.
            if hash_redirect_without_hash in self.doc_pages:
                file = self.doc_pages[hash_redirect_without_hash]
                dest_hash_path = get_relative_html_path(
                    page_old, file.url + new_hash, use_directory_urls
                )
                hash_redirects[i] = (old_hash, dest_hash_path)

        for old_hash, new_link in hash_redirects:
            log.info(f"Injecting redirect for '{page_old}{old_hash}' to '{new_link}'")

        js_redirects = JS_INJECT_EXISTS.format(
            redirects=gen_anchor_redirects(hash_redirects)
        )
        return js_redirects + html

    # Create HTML files for redirects after site dir has been built
    def on_post_build(self, config, **kwargs):
        # Determine if 'use_directory_urls' is set
        use_directory_urls = config.get("use_directory_urls")
        for page_old, redirect_entry in self.redirect_entries.items():
            page_old_without_hash, _ = _split_hash_fragment(str(page_old))
            # If the old page is a valid document page, it was injected in `on_page_content`.
            if page_old_without_hash in self.doc_pages:
                continue

            # Need to remove hash fragment from new page to verify existence
            page_new = redirect_entry["overall"]
            page_new_without_hash, new_hash = _split_hash_fragment(str(page_new))

            # External redirect targets are easy, just use it as the target path
            if page_new.lower().startswith(("http://", "https://")):
                dest_path = page_new

            # If the redirect target is a valid internal page, we need to create a relative path
            elif page_new_without_hash in self.doc_pages:
                file = self.doc_pages[page_new_without_hash]
                dest_path = get_relative_html_path(
                    page_old, file.url + new_hash, use_directory_urls
                )

            # If the redirect target isn't external or a valid internal page, throw an error
            # Note: we use 'warn' here specifically; mkdocs treats warnings specially when in strict mode
            else:
                log.warning("Redirect target '%s' does not exist!", page_new)
                continue

            # Fixup all the individual hash link references to be relative.
            hash_redirects = redirect_entry["hashes"]
            for i in range(len(hash_redirects)):
                old_hash, new_link = hash_redirects[i]
                hash_redirect_without_hash, new_hash = _split_hash_fragment(new_link)
                # If we are redirecting to a page that exists, update the destination hash path.
                if hash_redirect_without_hash in self.doc_pages:
                    file = self.doc_pages[hash_redirect_without_hash]
                    dest_hash_path = get_relative_html_path(
                        page_old, file.url + new_hash, use_directory_urls
                    )
                    hash_redirects[i] = (old_hash, dest_hash_path)

            log.info(f"Creating redirect for '{page_old}' to '{dest_path}'")
            for old_hash, new_link in hash_redirects:
                log.info(f"Creating redirect for '{page_old}{old_hash}' to '{new_link}'")

            # Create a new HTML file for the redirect
            dest_path = get_relative_html_path(page_old, dest_path, use_directory_urls)
            write_html(
                config["site_dir"],
                get_html_path(page_old, use_directory_urls),
                dest_path,
                hash_redirects,
            )


def _split_hash_fragment(path):
    """
    Returns (path, hash-fragment)

    "path/to/file#hash" => ("/path/to/file", "#hash")
    "path/to/file"      => ("/path/to/file", "")
    """
    path, hash, after = path.partition("#")
    return path, hash + after
