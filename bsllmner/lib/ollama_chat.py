import ollama
import sys
import json
import re
from ..prompt import load_prompt
from .util import print_time


def chat_ollama(input_json, model, prompt_indices, verbose=False, test=False):
    prompts = load_prompt.parse_md()

    to = 10 if test else len(input_json)
    for i in range(0, to):
        input_bs = json.dumps(input_json[i])
        if i%10==0 and verbose and not test:
            print_time(str(i))

        messages = []
        for j in range(0, len(prompt_indices)):
            messages.append({
                "role": prompts[prompt_indices[j]]["role"],
                "content": prompts[prompt_indices[j]]["text"]
            })
        messages.append({"role": "user", "content": "\n" + input_bs})
        options = {"temperature": 0}
        response = ollama.chat(model=model, messages=messages, options=options)
        res_text = response["message"]["content"]

        res_text_json = ""
        if "{" in res_text:
            try:
                res_text_json = re.findall(r"\{[^}]*\}", res_text)[-1]
            except IndexError:
                res_text_json = '{"error": "IndexError"}'

        bs_id = input_json[i]["accession"]
        print(bs_id, res_text_json.replace("\n",""), res_text.replace("\n", " "), sep="\t")

    return


if __name__ == "__main__":
    prompts = load_prompt.parse_md()
    first_prompt = prompts["1"]
    print(first_prompt, file=sys.stderr)
