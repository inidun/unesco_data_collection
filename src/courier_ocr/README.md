# courier_ocr

## Prerequisites

### tesseract

Pull `tesseractshadow/tesseract4re`-image from Docker Hub.

    docker pull tesseractshadow/tesseract4re

### Poppler

`pdf2image` needs `Poppler`. On Linux (Ubuntu) install with:

    sudo apt install poppler-utils

## Command examples

tesseract run command

```shell
docker run --mount type=bind,source="$(pwd)",target=/home/work \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    --mount "type=bind,src=/etc/passwd,dst=/etc/passwd,readonly" \
    --mount "type=bind,src=/etc/group,dst=/etc/group,readonly" \
    --rm -it tesseractshadow/tesseract4re $@
```

Process image
    
    ./t4re ./data/012656engo0001-20.tif xyz -l eng
    # ./t4re FILE OUTPUTBASE [OPTIONS]