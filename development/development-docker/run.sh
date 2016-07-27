#!/bin/sh

docker build -t pyfi-devel .
docker run -it --rm -p 6667:6667 pyfi-devel
