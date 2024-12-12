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
    llm_conclusion = {}
    for line in llmout:
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


def select_metasraout(metasraout_filename, llm_conclusion):
    with open(metasraout_filename, "r") as f:
        for line in f:
            spline = line.split("\t")
            bs_id = spline[0]
            if bs_id not in llm_conclusion:
                print(line.strip())
            elif llm_conclusion[bs_id][0:5] != "CVCL:":
                print(line.strip())
            elif llm_conclusion[bs_id] == spline[3]:
                print(line.strip())
    return

def main():
    parser = argparse.ArgumentParser(description="Terms not selected by LLM-review process is removed from metasraout tsv.")
    parser.add_argument('input_metasraout_filename', help='MetaSRA output tsv file')
    parser.add_argument('input_llmout_review_filename', help='LLM output review tsv file')
    args = parser.parse_args()

    input_llmout = load_tsv(args.input_llmout_review_filename)
    llm_conclusion = parse_llmout(input_llmout)
    select_metasraout(args.input_metasraout_filename, llm_conclusion)
    return


if __name__ == "__main__":
    main()
