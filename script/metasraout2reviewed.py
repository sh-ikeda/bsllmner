import json
import argparse
import sys


def load_tsv(tsv_filename):
    tsv = []
    with open(tsv_filename, "r") as f:
        for line in f:
            tsv.append(line.split("\t"))
    return tsv


def load_json(json_filename):
    jsonl = []
    with open(json_filename, "r") as f:
        for line in f:
            jsonl.append(json.loads(line))
    return jsonl


def null2str(s):
    if s is None:
        return "(null)"
    elif s == "":
        return "(null str)"
    else:
        return s


def parse_llmout_tsv(llmout_tsv):
    llm_conclusion = {}
    for line in llmout_tsv:
        bs_id = line[0]
        llmout_json_str = line[1]

        if len(llmout_json_str) == 0:
            llm_conclusion[bs_id] = ""
        else:
            try:
                llmout_json = json.loads(llmout_json_str)
            except json.JSONDecodeError:
                llm_conclusion[bs_id] = ""
                continue

            if not "cell_line_id" in llmout_json:
                llm_conclusion[bs_id] = ""
            else:
                llm_conclusion[bs_id] = llmout_json["cell_line_id"]
    return llm_conclusion


def parse_llmout_jsonl(llmout_jsonl):
    llm_conclusion = {}
    for line in llmout_jsonl:
        bs_id = line["accession"]
        llm_conclusion[bs_id] = line["output"]["cell_line_id"]
    return llm_conclusion

def select_metasraout(metasraout_filename, llm_conclusion):
    checked_not_unique = set()
    with open(metasraout_filename, "r") as f:
        for line in f:
            spline = line.split("\t")
            bs_id = spline[0]
            if bs_id not in llm_conclusion:
                print(line.strip())
            elif llm_conclusion[bs_id][0:5] != "CVCL:":  # not unique
                if bs_id not in checked_not_unique:
                    for i in range(3, len(spline)):
                        spline[i] = ""
                    edited_line = "\t".join(spline)
                    print(edited_line.strip())
                    checked_not_unique.add(bs_id)
                continue
            elif llm_conclusion[bs_id] == spline[3]:
                print(line.strip())
    return

def main():
    parser = argparse.ArgumentParser(description="Terms not selected by LLM-review process is removed from metasraout tsv.")
    parser.add_argument('input_metasraout_filename', help='MetaSRA output tsv file')
    parser.add_argument('input_llmout_review_filename', help='LLM output review file')
    args = parser.parse_args()

    if args.input_llmout_review_filename.endswith(".tsv"):
        input_llmout_tsv = load_tsv(args.input_llmout_review_filename)
        llm_conclusion = parse_llmout_tsv(input_llmout_tsv)
    elif args.input_llmout_review_filename.endswith(".jsonl"):
        input_llmout_jsonl = load_json(args.input_llmout_review_filename)
        llm_conclusion = parse_llmout_jsonl(input_llmout_jsonl)
    else:
        print("Error: Unsupported input file type. .tsv or .jsonl are allowed.", file=sys.stderr)
        exit(1)
    select_metasraout(args.input_metasraout_filename, llm_conclusion)
    return


if __name__ == "__main__":
    main()
