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
        print "usage: awk -f calc_test_values.awk -v type=[atac|chip|all] TSV" > "/dev/stderr"
        exit_without_end = 1
        exit 1
    }
    # if (!col) {
    #     print "usage: awk -f calc_test_values.awk -v col=NUM TSV" > "/dev/stderr"
    #     exit 1
    # }
}

FNR==1{
    # print $(col)
    next
}

# $1!="ATAC-Seq" {
is_target_exptype($2) {
    if ($4==$7) {  # 定義された正解 == 評価対象の出力
        if ($7 ~ /^CVCL:/)
            tp++
        else
            tn++
    } else {
        if (!$7)                 # 正解があるのに出力していない場合
            _e++
        else if ($4 ~ /^CVCL:/)  # 正解の CVCL と出力の CVCL が違う場合
            db++
        else                     # 無が正解なのに出力した場合
            c_++
    }
}

# $1!="ATAC-Seq" {
# # {
#     if ($(col+1)=="TRUE") {
#         if ($col ~ /^CVCL:/)
#             tp++
#         else
#             tn++
#     } else {
#         if (!$col)
#             _e++
#         else if ($13 ~ /^CVCL:/)
#             db++
#         else
#             c_++
#     }
# }

END {
    if (!exit_without_end) {
        print "TP: "tp
        print "TN: "tn
        print "D B: "db
        print "C _: "c_
        print "_ E: "_e
        print "total:  " tp+tn+db+c_+_e
        print "precision: " tp/(tp+db+c_)
        print "recall: " tp/(tp+db+_e)
    }
}
