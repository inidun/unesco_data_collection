#!/bin/bash
# Run OCRmyPDF inside Docker container

image_name_tag="ocrmypdf_tesseract5:latest"

[ -z "$1" ] && set -- "--version"

if [ ! $(docker image inspect ${image_name_tag} >/dev/null 2>&1)$? -eq 0 ]; then
    echo "No such image ${image_name_tag}"
    exit 2
fi

docker run \
    --workdir /data -v "$PWD:/data" \
    --user "$(id -u):$(id -g)" \
    --mount "type=bind,src=/etc/passwd,dst=/etc/passwd,readonly" \
    --mount "type=bind,src=/etc/group,dst=/etc/group,readonly" \
    --rm -it ocrmypdf_tesseract5 $@