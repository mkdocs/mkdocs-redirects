"""
Copyright 2019-2022 DataRobot, Inc. and its affiliates.
All rights reserved.
"""
import logging
import os
import posixpath

from mkdocs import utils
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File

log = logging.getLogger("mkdocs.plugin.redirects")


def gen_anchor_redirects(anchor_list: list):
    """
    Generate a dictionary of redirects for anchors.

    :param anchor_list: A list of tuples containing old anchors and new links.
    :return: A string of JavaScript redirects for the anchors.
    """
    js_redirects = ''
    for old_anchor, new_link in anchor_list:
        # Create a JavaScript redirect for each anchor
        js_redirects += f"""
        if (window.location.hash === "#{old_anchor}") {{
            window.location.href = "{new_link}";
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
        {redirects}
        location.href = `{url}${anchor ? '#' + anchor : ''}`;
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


def write_html(site_dir, old_path, new_path, anchor_list):
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


class RedirectPlugin(BasePlugin):
    # Any options that this plugin supplies should go here.
    config_scheme = (
        ("redirect_maps", config_options.Type(dict, default={})),  # note the trailing comma
    )

    # Build a list of redirects on file generation
    def on_files(self, files, config, **kwargs):
        self.redirects = self.config.get("redirect_maps", {})

        # Validate user-provided redirect "old files"
        for page_old in self.redirects:
            if not utils.is_markdown_file(page_old):
                log.warning("redirects plugin: '%s' is not a valid markdown file!", page_old)

        # Build a dict of known document pages to validate against later
        self.doc_pages = {}
        for page in files.documentation_pages():  # object type: mkdocs.structure.files.File
            self.doc_pages[page.src_path.replace(os.sep, "/")] = page

        # Create a dictionary to hold anchor maps for redirects
        redirect_maps = {}
        for page_old, page_new in self.redirects.items():
            page_old_without_hash, old_hash = _split_hash_fragment(str(page_old))
            if page_old_without_hash not in redirect_maps:
                redirect_maps[page_old_without_hash] = {'hashes': []}
            if old_hash == "":
                redirect_maps[page_old_without_hash]['overall'] = page_new
            else:
                redirect_maps[page_old_without_hash]['hashes'].append((old_hash, page_new))

        # If a page doesn't have an overall redirect, use the first hash redirect
        for page_old, redirect_map in redirect_maps.items():
            if 'overall' not in redirect_map:
                redirect_maps[page_old]['overall'] = redirect_map['hashes'][0][1]

        self.redirect_maps = redirect_maps

    def on_page_content(self, html, page, config, files):
        print(page)
        if page not in self.redirect_maps:
            return html

        injection_point, after = html.split("</head>", 1)
        return injection_point + \
            JS_INJECT_EXISTS.format(redirects=gen_anchor_redirects(self.redirect_maps[page]['hashes'])) + \
                "</head>" + after

    # Create HTML files for redirects after site dir has been built
    def on_post_build(self, config, **kwargs):
        # Determine if 'use_directory_urls' is set
        use_directory_urls = config.get("use_directory_urls")
        for page_old, redirect_maps in self.redirect_maps.items():
            # Need to remove hash fragment from new page to verify existence
            page_new = redirect_maps['overall']
            page_old_without_hash, _ = _split_hash_fragment(str(page_old))
            page_new_without_hash, new_hash = _split_hash_fragment(str(page_new))

            # External redirect targets are easy, just use it as the target path
            if page_new.lower().startswith(("http://", "https://")):
                dest_path = page_new

            # If the redirect target is a valid internal page, we need to create a relative path
            elif page_new_without_hash in self.doc_pages:
                file = self.doc_pages[page_new_without_hash]
                dest_path = get_relative_html_path(page_old, file.url + new_hash, use_directory_urls)

            # If the redirect target isn't external or a valid internal page, throw an error
            # Note: we use 'warn' here specifically; mkdocs treats warnings specially when in strict mode
            else:
                log.warning("Redirect target '%s' does not exist!", page_new)
                continue

            if page_old_without_hash in self.doc_pages:
                # If the old page is a valid document page, it was injected in `on_page_content`.
                pass
            else:
                # Otherwise, create a new HTML file for the redirect
                dest_path = get_relative_html_path(page_old, dest_path, use_directory_urls)
                write_html(
                    config["site_dir"],
                    get_html_path(page_old, use_directory_urls),
                    dest_path,
                    redirect_maps['hashes'],
                )


def _split_hash_fragment(path):
    """
    Returns (path, hash-fragment)

    "path/to/file#hash" => ("/path/to/file", "#hash")
    "path/to/file"      => ("/path/to/file", "")
    """
    path, hash, after = path.partition("#")
    return path, hash + after
