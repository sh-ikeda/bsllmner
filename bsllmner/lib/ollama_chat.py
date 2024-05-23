import ollama
import sys
import json
import re
from ..prompt import load_prompt
from .util import print_time


def chat_ollama(input_json, model, prompt_index, prompt_file, verbose=False, test=False):
    if prompt_file:
        with open(prompt_file) as f:
            first_prompt = f.read()
    else:
        prompts = load_prompt.parse_md()
        first_prompt = prompts[prompt_index]

    to = 10 if test else len(input_json)
    for i in range(0, to):
        input_bs = json.dumps(input_json[i])
        if i%10==0 and verbose and not test:
            # print(input_bs, "\n", file=sys.stderr)
            print_time(str(i))

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
            try:
                res_text_json = re.findall(r"\{[^}]*\}", res_text)[-1]
            except IndexError:
                res_text_json = '{"error": "IndexError"}'
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


if __name__ == "__main__":
    prompts = load_prompt.parse_md()
    first_prompt = prompts["1"]
    print(first_prompt, file=sys.stderr)
