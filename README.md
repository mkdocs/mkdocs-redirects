# mkdocs-redirects
Open source plugin for Mkdocs page redirects

## Installing

> **Note:** This package requires MkDocs version 1.0.4 or higher. 

Install with pip:

```bash
pip install mkdocs-redirects
```

Enable the plugin in your `mkdocs.yml`:

```yaml
plugins:
    - search
    - redirects
```

## Using

In your `mkdocs.yml`, add a `redirects` block that maps the old page location to the new location:

```
redirects:
  'old': 'some/new_location'
  'something/before': 'another/moved/file'
```

Note that the `.html` extension should be omitted (and will be automatically appended).

The plugin will dynamically create `old.html` and `something/before.html` in your configured `site_dir` with
HTML that will include a meta redirect to the new page location.

The new location will also be appended with `.html` extension and is assumed to be relative to the root of the site.

For nested subfolders, the plugin will automatically create these directories in the `site_dir`.

## Contributing

- Pull requests are welcome.
- File bugs and suggestions in the Github Issues tracker.

## Releasing

```
    make release
```

It will prompt you for your PyPI user and password.

See:
- https://packaging.python.org/tutorials/packaging-projects/
- https://packaging.python.org/guides/migrating-to-pypi-org/
