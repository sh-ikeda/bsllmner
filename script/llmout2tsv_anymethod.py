import json
import argparse

def load_tsv(tsv_filename):
    tsv = []
    with open(tsv_filename, "r") as f:
        for line in f:
            tsv.append(line.split("\t"))
    return tsv


def null2str(s):
    if s is None:
        return "(null)"
    elif s == "":
        return "(null str)"
    else:
        return s


def parse_llmout(llmout):
    for line in llmout:
        llmout_dict = {}
        bs_id = line[0]
        llmout_dict["accession"] = bs_id
        llmout_json_str = line[1]
        llmout_raw = line[2].strip()
        genes = ""
        methods = ""
        if len(llmout_json_str) == 0:
            genes = "error: no json"
            methods = "error: no json"
        else:
            try:
                llmout_json = json.loads(llmout_json_str)
            except json.JSONDecodeError:
                genes = "error: invalid json"
                methods = "error: invalid json"
                print(bs_id, llmout_raw, genes, methods, sep="\t")
                continue

            if not isinstance(llmout_json, list):
                genes = "error: violation"
                methods = "error: violation"
            else:
                genes = ", ".join([null2str(x["gene"]) for x in llmout_json])
                methods = ", ".join([null2str(x["method"]) for x in llmout_json])
        # print(bs_id, llmout_raw, genes, methods, sep="\t")
        print(bs_id, genes, methods, sep="\t")
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_llmout_filename', help='LLM output tsv file')
    args = parser.parse_args()

    input_llmout = load_tsv(args.input_llmout_filename)
    parse_llmout(input_llmout)
    return


if __name__ == "__main__":
    main()
