#!/bin/sh

BASEDIR=$(dirname "$0")
virtualenv -p /usr/bin/python3 "$BASEDIR/venv"
$BASEDIR/venv/bin/pip install -r "$BASEDIR/requirements.txt"

# Install development requirements, if "devel" argument is set.
if [ "$1" == "devel" ]
then
    $BASEDIR/venv/bin/pip install -r "$BASEDIR/development/requirements.txt"
fi
