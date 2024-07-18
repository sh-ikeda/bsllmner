import ollama
import sys
import json
import re
import os
from collections import defaultdict
from ..prompt import load_prompt
from .util import print_time


class BsLlmProcess:
    def __init__(self, bs_json, model, prompt_indices):
        self.bs_json = bs_json
        self.model = model
        self.prompt_indices = prompt_indices
        self.prompts = self.load_prompt()
        return

    def load_prompt(self):
        fname = "prompt.md"
        dirname = os.path.dirname(os.path.abspath(__file__))
        prompts = {}
        with open(dirname + "/" + fname, "r") as f:
            current_id = ""
            is_first_line = False
            for line in f:
                if line[0] == "#":
                    current_id = re.sub("^# ", "", line).strip()
                    prompts[current_id] = {}
                    prompts[current_id]["text"] = ""
                    is_first_line = True
                elif is_first_line:
                    prompts[current_id]["role"] = line.strip()
                    is_first_line = False
                elif current_id != "":
                    prompts[current_id]["text"] += line

        for id in prompts:
            prompts[id]["text"] = prompts[id]["text"].strip()
        return prompts

    def construct_messages(self):
        messages = []
        for j in range(0, len(self.prompt_indices)):
            messages.append({
                "role": self.prompts[self.prompt_indices[j]]["role"],
                "content": self.prompts[self.prompt_indices[j]]["text"]
            })
        return messages

    def extract_json_from_llmout(self, llmout):
        res_text_json = ""
        if "{" in llmout:
            try:
                res_text_json = re.findall(r"\{[^}]*\}", llmout)[-1]
            except IndexError:
                res_text_json = '{"error": "IndexError"}'
        return res_text_json.replace("\n", "")


class BsNer(BsLlmProcess):
    def __init__(self, bs_json, model, prompt_indices):
        super().__init__(bs_json, model, prompt_indices)
        return

    def ner(self, verbose=False, test=False):
        to = 10 if test else len(self.bs_json)
        messages_base = self.construct_messages()
        for i in range(0, to):
            input_bs = json.dumps(self.bs_json[i], indent=2)
            if i%10==0 and verbose and not test:
                print_time(str(i))

            messages = messages_base
            messages[-1]["content"] += input_bs
            options = {"temperature": 0}
            response = ollama.chat(model=self.model, messages=messages, options=options)
            res_text = response["message"]["content"]

            bs_id = self.bs_json[i]["accession"]
            res_text_json = self.extract_json_from_llmout(res_text)
            print(bs_id, res_text_json, res_text.replace("\n", " "), sep="\t")
        return


class BsReview(BsLlmProcess):
    def __init__(self, bs_json, model, prompt_indices, metasra_tsv, llmner_tsv):
        super().__init__(bs_json, model, prompt_indices)
        self.metasra_tsv = metasra_tsv
        self.llmner_tsv = llmner_tsv
        self.llmner_dict =  self.parse_llmner_tsv()
        self.bs_cvcl_cands = self.collect_bs_cvcl_cands()

    def collect_bs_cvcl_cands(self):
        bs_cvcl_count = defaultdict(int)
        bs_cvcl_cands = defaultdict(list)
        with open(self.metasra_tsv, "r") as f:
            for line in f:
                spline = line.split("\t")
                bs_id = spline[0]
                if len(spline) <= 3 :
                    continue
                ont_term_id = spline[3]
                if ont_term_id.startswith("CVCL:"):
                    bs_cvcl_count[bs_id] += 1
                    bs_cvcl_cands[bs_id].append(json.loads(spline[9]))

        for bs_id in bs_cvcl_count:
            if bs_cvcl_count[bs_id] <= 1:
                del bs_cvcl_cands[bs_id]
        return bs_cvcl_cands

    def parse_llmner_tsv(self):
        llmner_dict = {}
        with open(self.llmner_tsv) as f:
            for line in f:
                spline = line.split("\t")
                bs_id = spline[0]
                extracted_json = "{}"
                if spline[1]:
                    extracted_json = spline[1]
                llmner_dict[bs_id] = {
                    "extracted_json": json.loads(extracted_json),
                    "full_output": spline[2].replace("  ", "\n ")
                }
        return llmner_dict

    def reformat_cvcl(self, cvcl):
        reformatted_dict = {}
        reformatted_dict["id"] = cvcl["id"]
        reformatted_dict["name"] = cvcl["name"]
        for syn in cvcl["synonyms"]:
            syn_type = syn["type"].lower() + "_synonyms"
            if not syn_type in reformatted_dict:
                reformatted_dict[syn_type] = []
            reformatted_dict[syn_type].append(syn["name"])
        reformatted_dict["xrefs"] = []
        for i in range(0, len(cvcl["xrefs"])):
            reformatted_dict["xrefs"].append(cvcl["xrefs"][i])
            if cvcl["xrefs_comments"][i] != "":
                reformatted_dict["xrefs"][-1] += " ! " + cvcl["xrefs_comments"][i]
        return reformatted_dict

    def review(self, verbose=False, test=False):
        base_messages = self.construct_messages()
        print_time("Total samples to review: ", len(self.bs_cvcl_cands))
        for bs in self.bs_json:
            bs_id = bs["accession"]
            if bs_id not in self.bs_cvcl_cands:
                continue
            messages = base_messages

            ## Output from LLM in extraction
            messages.insert(-1, {
                "role": "assistant",
                "content": self.llmner_dict[bs_id]["full_output"]
            })

            ## Input of BioSample json
            messages[3]["content"] += json.dumps(bs, indent=2)

            ## Candidate evaluation
            ### Replace "{{cell_line}}" in the prompt with this cell line name
            messages[-1]["content"] = messages[-1]["content"].replace("{{cell_line}}", "\""+self.llmner_dict[bs_id]["extracted_json"]["cell_line"]+"\"")
            ### Input of candidate terms
            for cvcl_cand in self.bs_cvcl_cands[bs_id]:
                cvcl_id = cvcl_cand["id"].replace(":", "_")
                messages[-1]["content"] += "\n```json: " + cvcl_id + ".json\n" + json.dumps(self.reformat_cvcl(cvcl_cand), indent=2) + "\n```\n"

            ## Ask LLM
            options = {"temperature": 0}
            response = ollama.chat(model=self.model, messages=messages, options=options)
            res_text = response["message"]["content"]
            print("# ", bs_id)
            print(res_text)

        return


if __name__ == "__main__":
    prompts = load_prompt.parse_md()
    first_prompt = prompts["1"]
    print(first_prompt, file=sys.stderr)
