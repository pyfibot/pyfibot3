#!/bin/sh

BASEDIR=$(dirname "$0")
$BASEDIR/venv/bin/py.test --ignore="$BASEDIR/venv" -sv
