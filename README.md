# mkdocs-redirects

Plugin for [`mkdocs`](https://www.mkdocs.org/) to create page redirects (e.g. for moved/renamed pages).

Initially developed by [DataRobot](https://www.datarobot.com/).

## Installing

> **Note:** This package requires MkDocs version 1.0.4 or higher.

Install with pip:

```bash
pip install mkdocs-redirects
```

## Using

To use this plugin, specify your desired redirects in the plugin's `redirect_maps` setting in your `mkdocs.yml`:

```yaml
plugins:
    - redirects:
        redirect_maps:
            'old.md': 'new.md'
            'old/file.md': 'new/file.md'
            'some_file.md': 'http://external.url.com/foobar'
```

_Note: don't forget that specifying the `plugins` setting will override the defaults if you didn't already have it set! See [this page](https://www.mkdocs.org/user-guide/configuration/#plugins) for more information._

The redirects map should take the form of a key/value pair:

- The key of each redirect is the original _markdown doc_ (relative to the `docs_dir` path).
  - This plugin will handle the filename resolution during the `mkdocs build` process.
    This should be set to what the original markdown doc's filename was (or what it _would be_ if it existed), not the final HTML file rendered by MkDocs
- The value is the _redirect target_. This can take the following forms:
  - Path of the _markdown doc_ you wish to be redirected to (relative to `docs_dir`)
    - This plugin will handle the filename resolution during the `mkdocs build` process.
      This should be set to what the markdown doc's filename is, not the final HTML file rendered by MkDocs
  - External URL (e.g. `http://example.com`)

During the `mkdocs build` process, this plugin will create `.html` files in `site_dir` for each of the "old" file that redirects to the "new" path.
It will produce a warning if any problems are encountered or of the redirect target doesn't actually exist (useful if you have `strict: true` set).

### `use_directory_urls`

If you have `use_directory_urls: true` set (which is the default), this plugin will modify the redirect targets to the _directory_ URL, not the _actual_ `index.html` filename.
However, it will create the `index.html` file for each target in the correct place so URL resolution works.

For example, a redirect map of `'old/dir/README.md': 'new/dir/README.md'` will result in an HTML file created at `$site_dir/old/dir/index.html` which redirects to `../../new/dir/`.

Additionally, a redirect map of `'old/dir/doc_name.md': 'new/dir/doc_name.md'` will result in `$site_dir/old/dir/doc_name/index.html` redirecting to `../../new/dir/doc_name/`.

This mimics the behavior of how MkDocs builds the site dir without this plugin.

## Developing

### Setup a virtualenv

Create a virtualenv using a method of your choice.

```bash
brew install pyenv pyenv-virtualenv
pyenv install 2.7.18
pyenv virtualenv 2.7.18 mkdocs-redirects
pyenv activate mkdocs-redirects
```

### Build

```bash
make build
```

### Test

```bash
make test
```

## Releasing

```bash
make release
```

It will prompt you for your PyPI user and password.

See:

- <https://packaging.python.org/tutorials/packaging-projects/>
- <https://packaging.python.org/guides/migrating-to-pypi-org/>
