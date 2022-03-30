1.0.4 (2022-03-30)
------------------

- Transferred ownership of the package to mkdocs organization.
- Fix regression from 1.0.2 when handling index pages with `use_directory_urls: false` (#25)
- Fix the content of produced redirect pages on Windows (#34)

1.0.3 (2021-04-29)
------------------

- Fix crash on redirect targets to `index.md` or `README.md` with `use_directory_urls: true` (#21)

1.0.2 (2021-04-23)
------------------

- Use relative paths for redirects (#19)
- Fix for python 2/3 compatibility.

1.0.1 (2020-05-31)
------------------

- Fixes path separator for Windows. (#9)
- Use site_url as root for redirect paths. (#12)
- Make redirects more SEO friendly (set canonical rel link, noindex for robots) (#7)
