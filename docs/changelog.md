# Changelog

Changes to the `bsync` package by version tag

- 1.2.0
  - Changing `PATHS` seperator to two colons `::` instead of one to allow Windows named drive paths

- 1.1.0
  - Do not use the as-user enterprise header. Works for regular user apps now using a service account.
  - remove deprecated `--user` flag
  - added docs about service account collaboration

- 1.0.1
  - Added Windows to handle click Path args as strings or bytes (win cmd)
  - Improve sync performance and reduce complexity
  - Sphinx docs

- 0.1.1
  - Initial release
