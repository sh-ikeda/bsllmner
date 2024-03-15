import json
import argparse
import re


def load_json(json_filename):
    with open(json_filename, "r") as f:
        input_json = json.load(f)
    return input_json


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
        llmout_dict["accession"] = line[0]
        llmout_json_strs = re.findall(r"\{[^}]*\}", line[1])
        llmout_json = {}
        if llmout_json_strs:
            llmout_json = json.loads(llmout_json_strs[-1])
        llmout_dict["characteristics"] = llmout_json
        llmout_dicts.append(llmout_dict)
    return llmout_dicts


def repl_characteristics(input_json, llmout_dicts):
    replaced = []
    id2attr = {}
    for bs in input_json:
        id2attr[bs["accession"]] = bs
    for d in llmout_dicts:
        new_characteristics = {}
        # print(d)
        for k, v in d["characteristics"].items():
            new_characteristics[k] = [{"text": v}]
        id2attr[d["accession"]]["characteristics"] = new_characteristics
        replaced.append(id2attr[d["accession"]])
    return replaced


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_json_filename', help='BioSample JSON file')
    parser.add_argument('input_llmout_filename', help='LLM output tsv file')

    args = parser.parse_args()

    input_json = load_json(args.input_json_filename)
    input_llmout = load_tsv(args.input_llmout_filename)
    llmout_dicts = parse_llmout(input_llmout)
    print(json.dumps(repl_characteristics(input_json, llmout_dicts)))
    return


if __name__ == "__main__":
    main()
