#!/bin/bash

[ $# -eq 0 ] && { echo "Usage: $0 <dir> [options]"; exit 1; }

dir="$1"
if [[ ! -d "$dir" ]]; then
    echo "Error: $dir not found"
    exit 11
fi

# Create output directory if not exists
output_dir="output"
mkdir -p $output_dir

# Arguments to pass to pdfbox
args="${@:2}"

for file in $dir/*.pdf;
do
    bname=$(basename "$file" | cut -d. -f1)
    echo "Processing $bname"

    pages=$(pdfinfo $file | awk '/^Pages:/ {print $2}')

    output_file="${output_dir}/${bname}.xml"
    rm -f $output_file
    touch $output_file

    echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" >> $output_file
    echo "<document id=\"${bname:0:9}\">" >> $output_file

    for page in $(seq $pages);
    do
        java -jar pdfbox-app-2.0.22.jar ExtractText -startPage $page -endPage $page $args "$file" "/tmp/${bname}${page}.txt"
        echo -e "<page number=\"${page}\">\n<![CDATA[" >> $output_file
        cat "/tmp/${bname}${page}.txt" >> $output_file
        echo -e "]]>\n</page>" >> $output_file
        rm -f "/tmp/${bname}${page}.txt"
    done
    echo -e "\n</document>" >> $output_file
done