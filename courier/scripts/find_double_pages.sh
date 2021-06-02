#!/bin/bash
[ $# -eq 0 ] && { echo "Usage: $0 <dir>"; exit 1; }

dir="$1"
if [[ ! -d "$dir" ]]; then
    echo "Error: $dir not found"
    exit 11
fi

output_dir=double_pages
mkdir -p $output_dir/images
output_file=$output_dir/double_pages.txt
touch $output_file

for filename in $dir/*.pdf; do
    page_number=`pdfinfo -box -f 1 -l 999999 "$filename" 2>/dev/null | grep size | grep Page | awk '{ if ($4 / $6 > 1) {print $2 } }'`
    if [ "$page_number" != ""  ]; then
        echo $(basename $filename) $page_number
        echo $filename $page_number >> $output_file
        for page in $page_number; do
            `pdftoppm -q -jpeg -f $page -l $page $filename $output_dir/images/$(basename $filename)`
        done
    fi
done