### 

function is_target_exptype(exptype) {
    if (type == "atac") {
        if (exptype == "ATAC-Seq")
            return 1
        else
            return 0
    } else if (type == "chip") {
        if (exptype != "ATAC-Seq")
            return 1
        else
            return 0
    } else if (type == "all") {
        return 1
    } else {
        print "error: is_target_exptype: unexpected type" > "/dev/stderr"
        exit_without_end = 1
        exit 1
    }
}

BEGIN {
    FS = "\t"
    OFS = "\t"
    exit_without_end = 0
    if (!type) {
        print "usage: awk -f calc_precision.awk -v type=[atac|chip|all] <answers> <metasraout>" > "/dev/stderr"
        exit_without_end = 1
        exit 1
    }
}

# answers.tsv
FNR==NR && FNR!=1 {
    exptype_of_sample[$1] = $2
    answer_of_sample[$1] = $4
}

# metasraout.tsv
FNR!=NR && is_target_exptype(exptype_of_sample[$1]) {
    if ($4 ~ /^CVCL:/) {
        is_cvcl_mapped_sample[$1] = 1
        if ($4 == answer_of_sample[$1]) {
            tp_cvcl++
            # print $1
        } else {
            fp_cvcl++
        }
    }
}

END {
    if (!exit_without_end) {
        # process for samples not mapped to CVCL
        for (sample in answer_of_sample) {
            if (is_target_exptype(exptype_of_sample[sample]) &&
                !is_cvcl_mapped_sample[sample]) {       # output is "not mapped to CVCL"
                if (answer_of_sample[sample] == "") {
                    tp_notcvcl++
                } else {
                    fp_notcvcl++
                }
            }
        }
        print "TP_CVCL: "tp_cvcl        # Correctly output CVCL
        print "TP_notCVCL: "tp_notcvcl  # Correctly no output
        print "FP_CVCL: "fp_cvcl        # Wrongly output CVCL
        print "FP_notCVCL: "fp_notcvcl  # Wrongly no output
        tp = tp_cvcl + tp_notcvcl
        fp = fp_cvcl + fp_notcvcl
        print "total:  " tp+fp
        print "precision: " tp/(tp+fp)
        print "precision for CVCL: " tp_cvcl/(tp_cvcl+fp_cvcl)
    }
}
