import json
import argparse

def load_tsv(tsv_filename):
    tsv = []
    with open(tsv_filename, "r") as f:
        for line in f:
            tsv.append(line.split("\t"))
    return tsv


def parse_llmout(llmout):
    for line in llmout:
        llmout_dict = {}
        bs_id = line[0]
        llmout_dict["accession"] = bs_id
        llmout_json_str = line[1]
        llmout_raw = line[2].strip()
        ko = ""
        kd = ""
        if len(llmout_json_str) == 0:
            ko = "error: no json"
            kd = "error: no json"
        else:
            try:
                llmout_json = json.loads(llmout_json_str)
            except json.JSONDecodeError:
                ko = "error: invalid json"
                kd = "error: invalid json"
                print(bs_id, llmout_raw, ko, kd, sep="\t")
                continue

            if "knockout" in llmout_json:
                ko = ", ".join(llmout_json["knockout"])
            else:
                ko = "error: no knockout"
            if "knockdown" in llmout_json:
                kd = ", ".join(llmout_json["knockdown"])
            else:
                kd = "error: no knockdown"
        print(bs_id, llmout_raw, ko, kd, sep="\t")
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
