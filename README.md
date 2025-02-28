# mkdocs-redirects

**Plugin for [`mkdocs`](https://www.mkdocs.org/) to create page redirects (e.g. for moved/renamed pages)**

Initially developed by [DataRobot](https://www.datarobot.com/).

[![PyPI](https://img.shields.io/pypi/v/mkdocs-redirects)](https://pypi.org/project/mkdocs-redirects/)
[![License](https://img.shields.io/github/license/mkdocs/mkdocs-redirects)](https://github.com/mkdocs/mkdocs-redirects/blob/master/LICENSE.md)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/mkdocs/mkdocs-redirects/ci.yml.svg)](https://github.com/mkdocs/mkdocs-redirects/actions?query=event%3Apush+branch%3Amaster)

## Installing

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

Alternatively, get the redirects from a seperate `yml` file with `map_file`.

```yaml
plugins:
  - redirects:
      map_file: 'redirect_map.yml'
```

Where the `map_file` uses the same syntax as above.

> **Note**  
> Don't forget that specifying the `plugins` setting will override the defaults if you didn't already have it set! See [this page](https://www.mkdocs.org/user-guide/configuration/#plugins) for more information.

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

Dev dependencies and tasks are managed with [Hatch](https://hatch.pypa.io/). Tasks run in their own environment, created on the fly if missing, in a separate directory tree.

To run all checks and fixes:

```bash
hatch run all
```

You can learn about individual commands from the output, or by inspecting `scripts` in [pyproject.toml](pyproject.toml).

## Releasing

A release is published to PyPI through GitHub Actions whenever a new tag is pushed.

So, to create a release, run `.tools/release.sh x.y.z` (which bumps the version in `__init__.py`, checks the build, creates a commit and a tag `vx.y.z`, and pushes it to GitHub).

Then fill out a GitHub release with release notes.
