#!/bin/bash
# ./find_odd_pages.sh > landscape_pages.txt 2>/dev/null
# FIXME: Add argument: folder

for filename in courier_pdfs/*.pdf; do
    page_number=`pdfinfo -box -f 1 -l 999999 "$filename" | grep size | grep Page | awk '{ if ($4 / $6 > 1) {print $2 } }'`
    if [ "$page_number" != ""  ]; then
        echo $filename $page_number
    fi
done