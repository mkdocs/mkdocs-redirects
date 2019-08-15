import logging
import os
import textwrap

from mkdocs import utils
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

log = logging.getLogger('mkdocs.plugin.redirects')
log.addFilter(utils.warning_filter)


def write_html(config, old_path, new_path):
    """ Write an HTML file in the site_dir with a meta redirect to the new page """
    old_path_abs = os.path.join(config['site_dir'], old_path)
    old_dir = os.path.dirname(old_path)
    old_dir_abs = os.path.dirname(old_path_abs)
    if not os.path.exists(old_dir_abs):
        log.debug("Creating directory '%s'", old_dir)
        os.makedirs(old_dir_abs)
    with open(old_path_abs, 'w') as f:
        log.debug("Creating redirect: '%s' -> '%s'",
                  old_path, new_path)
        f.write(textwrap.dedent(
            """
            <!doctype html>
            <html lang="en" class="no-js">
            <head>
                <script>var anchor=window.location.hash.substr(1);location.href="{url}"+(anchor?"#"+anchor:"")</script>
                <meta http-equiv="refresh" content="0; url={url}">
            </head>
            <body>
            Redirecting...
            </body>
            </html>
            """
        ).format(url=new_path))


def get_html_path(path, use_directory_urls):
    """ Return the HTML file path for a given markdown file """
    parent, filename = os.path.split(path)
    name_orig, ext = os.path.splitext(filename)
    if use_directory_urls:
        name = 'index' if name_orig.lower() in ('index', 'readme') else name_orig
        if name == 'index':
            return os.path.join(parent, 'index.html')
        else:
            return os.path.join(parent, name, 'index.html')
    else:
        return os.path.join(parent, (name_orig + '.html'))


class RedirectPlugin(BasePlugin):
    config_scheme = (
        ('redirect_maps', config_options.Type(dict, default={})),  # note the trailing comma
    )

    # Build a list of redirects on file generation
    def on_files(self, files, config, **kwargs):
        self.redirects = self.config.get('redirect_maps', {})

        # Validate user-provided redirect "old files"
        for page_old in self.redirects.keys():
            if not utils.is_markdown_file(page_old):
                log.warn("redirects plugin: '%s' is not a valid markdown file!", page_old)

        # Build a dict of known document pages
        self.doc_pages = {}
        for page in files.documentation_pages():  # object type: mkdocs.structure.files.File
            self.doc_pages[page.src_path] = page

    # Create HTML files for redirects after site dir has been built
    def on_post_build(self, config, **kwargs):
        # Determine if 'use_directory_urls' is set; our destination
        use_directory_urls = config.get('use_directory_urls')

        for page_old, page_new in self.redirects.items():

            if page_new.lower().startswith(('http://', 'https://')):
                dest_path = page_new

            elif page_new in self.doc_pages:
                dest_path = '/' + self.doc_pages[page_new].dest_path
                if use_directory_urls:
                    dest_path = dest_path.split('index.html')[0]

            else:
                log.warn("Redirect target '%s' does not exist!", page_new)
                continue

            write_html(config,
                       get_html_path(page_old, use_directory_urls),
                       dest_path)
