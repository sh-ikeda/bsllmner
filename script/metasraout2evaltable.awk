## usage: awk -f metasraout2evaltable.awk <metasraout.tsv> <answers.tsv>
### The second tsv is assumed to have BioSample IDs in the first column.

BEGIN {
    OFS = FS = "\t"
}

FNR==NR && $4~/^CVCL/ {
    a[$1] = $3 "\t" $4 "\t" $5 "\t" $9
    if (b[$1]++) {
        a[$1] = "not unique\tnot unique"
    }
}

FNR!=NR {
    print $0, a[$1]
}
