1.0.3 (unreleased)
------------------

- Fix crash on redirect targets to `index.md` or `README.md` with `use_directory_urls: true`: https://github.com/datarobot/mkdocs-redirects/pull/21

1.0.2 (2021-04-23)
------------------

- Use relative paths for redirects: https://github.com/datarobot/mkdocs-redirects/pull/19
- Fix for python 2/3 compatibility.

1.0.1 (2020-05-31)
------------------

- Fixes path separator for Windows.
- Use site_url as root for redirect paths.
- Make redirects more SEO friendly (set canonical rel link, noindex for robots)
