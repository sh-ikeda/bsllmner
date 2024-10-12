### 

BEGIN {
    FS = "\t"
    OFS = "\t"
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
{
    if ($3==$6) {  # 定義された正解 == 評価対象の出力
        if ($6 ~ /^CVCL:/)
            tp++
        else
            tn++
    } else {
        if (!$6)                 # 正解があるのに出力していない場合
            _e++
        else if ($3 ~ /^CVCL:/)  # 正解の CVCL と出力の CVCL が違う場合
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
    print "TP: "tp
    print "TN: "tn
    print "D B: "db
    print "C _: "c_
    print "_ E: "_e
    print "total:  " tp+tn+db+c_+_e
    print "precision: " tp/(tp+db+c_)
    print "recall: " tp/(tp+db+_e)
}
