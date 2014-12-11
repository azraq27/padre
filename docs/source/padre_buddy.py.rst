padre_buddy.py - Your friendly command-line helper
===================================================

Usage:
----------

padre_buddy.py [-h] [--quiet] [-s SUBJECT] [-n SESSION] [-t TYPE]
                      [-l LABEL] [-e EXPERIMENT]
                      {info,list,link} ...

optional arguments::

  -h, --help            show this help message and exit
  --quiet, -q           just print the bare information (good for scripts)

explicitly specify object::

  (certain commands are also able to parse fuzzy keyword arguments)

  -s SUBJECT, --subject SUBJECT
                        subject id
  -n SESSION, --session SESSION
                        session identifier, by convention date of the scanning
                        session in the format YYYYMMDD, but could really be
                        any unique string
  -t TYPE, --type TYPE  session type
  -l LABEL, --label LABEL
                        label for dataset (the type of dataset; anatomy,
                        sdtones)
  -e EXPERIMENT, --experiment EXPERIMENT
                        experiment identifier

commands::

    :info:                get details on a single object
    :list:                retrieve a list of things
    :link:                create symbolic links in the current directory to
                          datasets matching the given parameters