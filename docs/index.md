# bsync 0.1.1 documentation

## Purpose

Sync files from your computer to Box.com using the Box API

Think rsync for Box

```{note}
Right now, this only syncs your folder to Box and not Box to your folder
```

## Install

`pip install bsync`

## Features

- Preserves directory structure when uploading
- Define which files to sync base on glob expressions
- Can handle large files with chunked upload support
  - Large files are uploaded with a progress bar indicator
- Reports what's been uploaded in a CSV artifact


```{toctree}
box.app.setup
usage
api
```
