import logging
import os
import textwrap

from mkdocs import utils as mkdocs_utils
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File

log = logging.getLogger(__name__)
log.addFilter(mkdocs_utils.warning_filter)


class RedirectPlugin(BasePlugin):

    def on_post_build(self, config, **kwargs):
        redirects = config.get('redirects', {})

        for old_page, new_page in redirects.iteritems():
            old_page_path = os.path.join(config['site_dir'], '{}.html'.format(old_page))
            new_page_path = os.path.join(config['site_dir'], '{}.html'.format(new_page))

            # check that the page being redirected to actually exists
            if not os.path.exists(os.path.dirname(new_page_path)):
                msg = 'Redirect does not exist for path: {}'.format(new_page_path)
                if config.get('strict', False):
                    raise Exception(msg)
                else:
                    log.warn(msg)

            # ensure the folder path exists, recursively for nested directories.
            if not os.path.exists(os.path.dirname(old_page_path)):
                os.makedirs(os.path.dirname(old_page_path))

            # write an HTML file in the site_dir with a meta redirect to the new page
            # note that it will prefix the path with `/` to be relative to the site root.
            with open(old_page_path, 'w') as f:
                f.write(textwrap.dedent("""
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
                """).format(url='/{}.html'.format(new_page)))
