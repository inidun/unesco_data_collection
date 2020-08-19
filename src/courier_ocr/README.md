#!/bin/bash

chmod +x t4re

docker pull tesseractshadow/tesseract4re

./t4re --help
./t4re -l eng ./data/012656engo0001-20.tif xyz

docker run --mount type=bind,source="$(pwd)",target=/home/work \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    --mount "type=bind,src=/etc/passwd,dst=/etc/passwd,readonly" \
    --mount "type=bind,src=/etc/group,dst=/etc/group,readonly" \
    --rm -it tesseractshadow/tesseract4re $@
