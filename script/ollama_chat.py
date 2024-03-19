import ollama
import sys
import json
import datetime
import argparse
import re


def chat_ollama(input_json, model, prompt_index, verbose=False, test=False):
    if verbose:
        print(first_prompt, file=sys.stderr)

    to = 10 if test else len(input_json)
    for i in range(0, to):
        input_bs = json.dumps(input_json[i])
        if verbose:
            print(input_bs, "\n", file=sys.stderr)

        messages = [
            {"role": "user", "content": first_prompt},
            {"role": "assistant", "content": "Yes."},
        ]
        # for j in range(0, len(examples)):
        #     messages.append({"role": "user", "content": examples[j]})
        #     messages.append({"role": "assistant", "content": answers[j]})
        messages.append({"role": "user", "content": "Think step by step for the data below.\n" + input_bs})
        response = ollama.chat(model=model, messages=messages)
        res_text = response["message"]["content"]
        # messages.append(response["message"])

        res_text_json = ""
        # confirm = ""
        if "{" in res_text:
            #res_text_json = re.search(r"\{[^}]*\}", res_text).group()
            res_text_json = re.findall(r"\{[^}]*\}", res_text)[-1]
        # if len(res_text_json) > 0:
        #     cell_line = re.findall(r'"[^"]*"', res_text_json)[1]
        #     if cell_line != "\"None\"":
        #         prompt = f"You are a bot just answers to my question with 'yes' or 'no'. I will input JSON formatted data that is metadata of a sample for a biological experiment. Answer whether {cell_line} is differentiated or transdifferentiated into another type of cells. Your answer must be just one word, 'yes' or 'no'. Are you ready?"
        #         messages = [
        #             {"role": "user", "content": prompt},
        #             {"role": "assistant", "content": "yes"},
        #             {"role": "user", "content": input_bs},
        #         ]
        #         response = ollama.chat(model=model, messages=messages)
        #         confirm = response["message"]["content"].replace("\n", " ")

        bs_id = input_json[i]["accession"]
        # print(bs_id, res_text.replace("\n", " "), confirm, sep="\t")
        print(bs_id, res_text_json.replace("\n",""), res_text.replace("\n", " "), sep="\t")

    return


def load_json(json_filename):
    with open(json_filename, "r") as f:
        input_json = json.load(f)
    return input_json


def print_time():
    ct = datetime.datetime.now()
    print(f"[{ct}]\n", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename', help='BioSample JSON file')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-m', '--model')
    parser.add_argument('-p', '--prompt')
    args = parser.parse_args()

    input_json = load_json(args.input_filename)
    verbose = args.verbose
    test = args.test
    model = args.model
    prompt_index = args.prompt
    print_time()
    chat_ollama(input_json, model, prompt_index, verbose, test)
    print_time()
    return


if __name__ == "__main__":
    main()
