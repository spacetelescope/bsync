# bsync
Sync files from your computer to Box.com using the Box API

Think rsync for Box

## Features

- Preserves directory structure when uploading
- Define which files to sync base on glob expressions
- Can handle large files with chunked upload support
  - Large files are uploaded with a progress bar indicator
- Reports what's been uploaded in a CSV artifact

## Install

`pip install bsync`

Now the `bsync` command should be available in your shell (`bsync.exe` for Win)

## Documentation

Please see the official documentation for more information and usage

[https://bsync.readthedocs.io/en/latest/](https://bsync.readthedocs.io/en/latest/)
