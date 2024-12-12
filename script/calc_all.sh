#! /bin/bash
set -euo pipefail

answer_tsv=$1
shift

script_dir=$(cd $(dirname $BASH_SOURCE); pwd)
types=("all" "atac" "chip")

for f in "$@"; do
    for type in "${types[@]}" ; do
        awk -f $script_dir/calc_accuracy.awk -v type=$type $answer_tsv $f | awk 'FNR<=4{printf $0 "\t"}'
        awk -f $script_dir/calc_coverage.awk -v type=$type $f $answer_tsv | awk 'FNR<=4{printf $0 "\t"}'
        echo ""
    done
done
