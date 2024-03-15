import json
import argparse
import re
import sys

def load_tsv(tsv_filename):
    tsv = []
    with open(tsv_filename, "r") as f:
        for line in f:
            tsv.append(line.split("\t"))
    return tsv


def parse_llmout(llmout):
    llmout_dicts = []
    for line in llmout:
        llmout_dict = {}
        bs_id = line[0]
        llmout_dict["accession"] = bs_id
        llmout_json_strs = re.findall(r"\{[^}]*\}", line[1])
        llmout_json = {}
        if llmout_json_strs:
            try:
                llmout_json = json.loads(llmout_json_strs[-1].replace("\\_", "_"))
                # In minor cases, LLM might include null values in output JSON.
                keys_to_delete = [k for k, v in llmout_json.items() if v is None]
                for key in keys_to_delete:
                    del llmout_json[key]
            except json.decoder.JSONDecodeError:
                print(f"Warning: JSON malformed: {bs_id}: {llmout_json_strs[-1]}", file=sys.stderr)
        llmout_dict["characteristics"] = llmout_json
        llmout_dicts.append(llmout_dict)
    return llmout_dicts


def print_llmout_tsv(llmout_dicts):
    sp_keys = ["tissue", "host_tissue", "differentiated_from",
               "differentiated_into", "cell_type", "cell_line", "disease"]
    print("BioSample ID", "\t".join(sp_keys), "others", sep="\t")
    for d in llmout_dicts:
        newline = []
        newline.append(d["accession"])
        for spk in sp_keys:
            newline.append(d["characteristics"].get(spk, ""))
        others = ""
        for k, v in d["characteristics"].items():
            if k not in sp_keys:
                others += f'{k}: {v}, '
        newline.append(others.strip(", "))
        print("\t".join(newline))
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_llmout_filename', help='LLM output tsv file')
    args = parser.parse_args()

    input_llmout = load_tsv(args.input_llmout_filename)
    llmout_dicts = parse_llmout(input_llmout)
    print_llmout_tsv(llmout_dicts)
    return


if __name__ == "__main__":
    main()
