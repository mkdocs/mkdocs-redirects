import os

from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File


class RedirectPlugin(BasePlugin):

    def __init__(self):
        self.temp_files = []
        super(RedirectPlugin, self).__init__()

    def on_files(self, files, config, **kwargs):
        redirects = config.get('redirects', {})
        if not redirects:
            return files

        for old_page, new_page in redirects.iteritems():
            # construct markdown file content with meta redirect
            old_page_path = os.path.join(config['docs_dir'], '{}.md'.format(old_page))
            new_page_path = os.path.join(config['docs_dir'], '{}.html'.format(new_page))

            # ensure the folder path exists, recursively for nested directories.
            if not os.path.exists(os.path.dirname(old_page_path)):
                os.makedirs(os.path.dirname(old_page_path))

            # write the file content for the old Markdown file, with a meta redirect to the new page
            with open(old_page_path, 'w') as f:
                f.write('redirect: {}'.format('{}.html'.format(new_page)))

            # keep track of these temp markdown files so we can clean them up after the build
            self.temp_files.append(old_page_path)

            old_markdown = File(old_page_path, config['docs_dir'], config['site_dir'], config['use_directory_urls'])
            files.append(old_markdown)

        return files

    def on_post_build(self, config, **kwargs):
        for f in self.temp_files:
            if os.path.exists(f):
                os.unlink(f)
        # note: does not clean up temporary directories that were created to contain these files
