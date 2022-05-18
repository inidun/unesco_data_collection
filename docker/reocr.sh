#!/bin/bash

max_procs=1
uuid=$(uuidgen | sed 's/.*-//')

ocrmypdf=./ocrmypdf.sh 
[[ -f $ocrmypdf ]] || { echo "Script not found: $ocrmypdf" && exit 2; }

ocr_args="-l eng --force-ocr --clean --deskew \
    --optimize 3 --jbig2-lossy --pdfa-image-compression jpeg \
    --tesseract-pagesegmode 1 --tesseract-oem 1 --tesseract-thresholding sauvola \
    --tesseract-timeout 4800 --verbose"

function usage()
{
    echo "Usage: $0 --input-folder FOLDER [--output-folder FOLDER] [--max-procs N]"
}

POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        --input-folder|-i)
            input_folder="$2"; shift; shift
        ;;
        --output-folder|-o)
            output_folder="$2"; shift; shift
        ;;
        --max-procs|-p)
            max_procs="$2"; shift; shift
        ;;
        --help|-h)
            usage ;
            exit 0
        ;;
        *)
        POSITIONAL+=("$1")
        shift
        ;;
    esac
done

set -- "${POSITIONAL[@]}" # restore positional parameters

if [ ! -d "$input_folder" ]; then
    echo "Error: input folder doesn't exist"
    usage
    exit 2
fi

if [ ! "$(find $input_folder -maxdepth 1 -type f | grep -i '.*\.pdf$')" ]; then
    echo "Error: no PDF-files in input folder"
    exit 2
fi

if [[ $max_procs < 1 || $max_procs > 6 ]]; then
    echo "Error: max procs bust be an integer between 1 and 6" ;
    exit 75
fi

if [ "$output_folder" == "" ]; then
    output_folder=${input_folder}/output
    echo "Info: target folder not specified, using: ${output_folder}" ;
fi

log_dir=$output_folder/logs
pdf_dir=$output_folder/pdf
txt_dir=$output_folder/txt
org_dir=$output_folder/original
mkdir -p $log_dir
mkdir -p $pdf_dir
mkdir -p $txt_dir
mkdir -p $org_dir

echo "[$(date +%FT%T)] Batch job started (id=$uuid)" >> $log_dir/time.log
echo "[$(date +%FT%T)] Running ocrmydf with arguments: $ocr_args" | tr -s ' ' >> $log_dir/time.log

if [[ $max_procs > 1 ]]; then

    command_file="$log_dir/commands_${uuid}.txt"
    echo "command file: $command_file"
    rm -rf $command_file

    for file in $input_folder/*.pdf; do

        basename=$(basename "$file" .pdf)

        time="/usr/bin/time -ao $log_dir/time.log -f \\\"[\$(date +%FT%T)] Processed ${basename}.pdf in:\\\t%E\\\""

        echo "$time $ocrmypdf $ocr_args --sidecar $txt_dir/${basename}.txt $file $pdf_dir/${basename}.pdf | tee $log_dir/${basename}_${uuid}.log && mv --backup=numbered $file $org_dir/${basename}.pdf" >> ${command_file}

    done

    echo "info: running in parallel mode using $max_procs processes" | tee -a $log_dir/time.log

    cat $command_file | xargs -o -I CMD --max-procs=$max_procs bash -c CMD

    echo "Done"

else

    echo "info: running in sequential mode"

    for file in $input_folder/*.pdf; do

        basename=$(basename "$file" .pdf)
        if [ -e $txt_dir/${basename}.txt ]; then
            echo "[$(date +%FT%T)] Skipped ${basename}.pdf exists" >> $log_dir/time.log ;
            mv -f $file $org_dir/${basename}.pdf ;
            continue;
        fi

        /usr/bin/time -ao $log_dir/time.log -f "[$(date +%FT%T)] Processed ${basename}.pdf in:\t%E" $ocrmypdf $ocr_args --sidecar $txt_dir/${basename}.txt $file $pdf_dir/${basename}.pdf &> $log_dir/${basename}_${uuid}.log && mv --backup=numbered $file $org_dir/${basename}.pdf

    done

fi

echo "[$(date +%FT%T)] Batch job done (id=$uuid)" >> $log_dir/time.log

