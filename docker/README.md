# OCRmyPDF with Tesseract 5 and tessdata_best

Dockerfile for OCRmyPDF using Tesseract 5 and tessdata_best language packs.

## Build

    docker build -t ocrmypdf_tesseract5 .

## Run as a command line program

    docker run --rm -i ocrmypdf_tesseract5  - - <input.pdf >output.pdf [options...]

## Testing

    docker run --entrypoint python3 ocrmypdf_tesseract5 -m pytest

## Accessing Shell

    docker run -it --rm --entrypoint /bin/bash ocrmypdf_tesseract5

## Watcher

```sh
docker run \
  -v "$(pwd)/input":/input \
  -v "$(pwd)/output":/output \
  -e OCR_OUTPUT_DIRECTORY_YEAR_MONTH=0 \
  -e OCR_ON_SUCCESS_DELETE=0 \
  -e OCR_DESKEW=1 \
  -e PYTHONUNBUFFERED=1 \
  -e LOGLEVEL=2 \
  -e OCR_JSON_SETTINGS='{"language": "eng", "clean": true, "force_ocr": true, "optimize": 3, "jbig2_lossy": true, "tesseract_pagesegmode": 1, "tesseract_oem": 1,  "pdfa_image_compression": "jpeg", "tesseract_thresholding": "sauvola"}' \
  -it --rm --entrypoint python3 \
  ocrmypdf_tesseract5 \
  misc/watcher.py
```

