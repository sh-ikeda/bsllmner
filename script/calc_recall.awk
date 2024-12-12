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
        print "usage: awk -f calc_precision.awk -v type=[atac|chip|all] <metasraout> <answers>" > "/dev/stderr"
        exit_without_end = 1
        exit 1
    }
}

# metasraout.tsv
FNR==NR {
    if ($4 ~ /^CVCL:/) {
        in_output_answer[$1, $4] = 1
        in_output_sample[$1] = 1
    }
    # is_target_sample[$1] = is_target_exptype($2)
    # answer_of_sample[$1] = $4
}

# answers.tsv
FNR!=NR && FNR!=1 && is_target_exptype($2) {
    if ($4 ~ /^CVCL:/) {
        if (in_output_answer[$1, $4]) {
            tp_cvcl++
            #print $1
        } else {
            fn_cvcl++
        }
        # is_cvcl_mapped_sample[$1] = 1
        # if ($4 == answer_of_sample[$1]) {
        #     tp_cvcl++
        # } else {
        #     fp_cvcl++
        # }
    } else {
        if (in_output_sample[$1]) {
            fn_notcvcl++
        } else {
            tp_notcvcl++
        }
    }
}

END {
    if (!exit_without_end) {
        print "TP_CVCL: "tp_cvcl        # Correctly output CVCL
        print "TP_notCVCL: "tp_notcvcl  # Correctly no output
        print "FN_CVCL: "fn_cvcl        # Wrongly no output answer
        print "FN_notCVCL: "fn_notcvcl  # Wrongly output CVCL
        tp = tp_cvcl + tp_notcvcl
        fn = fn_cvcl + fn_notcvcl
        print "total:  " tp+fn
        print "recall: " tp/(tp+fn)
        print "recall for CVCL: " tp_cvcl/(tp_cvcl+fn_cvcl)
    }
}
