# bsync
Sync files from your computer to Box.com using the Box API

Think rsync for Box

Right now, this only syncs your folder to Box and not Box to your folder

## Install

`pip install bsync`

## Configuration

You need to create a Box app with access to writing files/folders.
The app must have JWT server side auth enabled.
The JSON settings file with your keys will be required to run this.

## Usage


```
$ bsync --help

Usage: bsync [OPTIONS] SOURCE_FOLDER BOX_FOLDER_ID

  Syncs the contents of local folder to your Box account

  SOURCE_FOLDER is the path of an existing folder

  BOX_FOLDER_ID is the ID for the folder in Box where you want the files sent

Options:
  -u, --box-user TEXT             User account name on Box.com. Defaults to
                                  jquick
  -s, --settings FILE
  -i, --ipdb                      Drop into ipdb shell on error
  -l, --log-level [critical|fatal|error|warn|warning|info|debug]
                                  Log level
  --log-file FILE                 Log file
  -o, --output TEXT               File to write created items as CSV report
  --help                          Show this message and exit
  ```
