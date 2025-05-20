import ollama
import json
import re
import os
import sys
import copy
import yaml
from collections import defaultdict
from .util import print_time
from .util import extract_last_json
from openai import OpenAI


class BsLlmProcess:
    def __init__(self, bs_json, model, prompt_filename, prompt_indices, host_url="", server="ollama"):
        self.bs_json = bs_json
        self.model = model
        self.prompt_indices = prompt_indices
        self.prompts = self.load_prompt(prompt_filename)
        self.host_url = host_url
        self.is_input_ebi_format = True
        self.llm_input_json = self.construct_llm_input_json()
        self.server = server
        if server == "ollama":
            self.client = ollama.Client(host=host_url)
        elif server == "vllm":
            self.client = OpenAI(base_url=host_url, api_key="EMPTY")
        else:
            print("Error: Invalid server: ", server, file=sys.stderr)
            exit(1)
        return

    def load_prompt(self, prompt_filename):
        if prompt_filename == "":
            dirname = os.path.dirname(os.path.abspath(__file__))
            prompt_filepath = dirname + "/../prompt/" + "prompt.yaml"
        else:
            prompt_filepath = prompt_filename

        with open(prompt_filepath, "r") as f:
            prompts = yaml.safe_load(f)

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

    def construct_llm_input_json(self):
        # convert input biosample json into minimized format for LLM input
        dirname = os.path.dirname(os.path.abspath(__file__))
        filter_filepath = dirname + "/../metadata/" + "filter_key_val_rules.json"
        with open(filter_filepath, "r") as f:
            filter_key_val = json.load(f)

        llm_input_json = []
        if "characteristics" in self.bs_json[0] and isinstance(self.bs_json[0]["characteristics"], dict):
            self.is_input_ebi_format = True
        else:
            self.is_input_ebi_format = False

        if self.is_input_ebi_format:
            for i in range(0, len(self.bs_json)):
                sample = self.bs_json[i]
                attrs = self.bs_json[i]["characteristics"]
                llm_input_json.append({})
                for k, v in attrs.items():
                    if k not in filter_key_val["filter_keys"]:
                        llm_input_json[i][k] = v[0]["text"]
        else:
            for i in range(0, len(self.bs_json)):
                sample = self.bs_json[i]
                llm_input_json.append({})
                for k, v in sample.items():
                    if k not in filter_key_val["filter_keys"]:
                        llm_input_json[i][k] = v

        return llm_input_json


class BsNer(BsLlmProcess):
    def __init__(self, bs_json, model, prompt_filename, prompt_indices, host_url, server):
        super().__init__(bs_json, model, prompt_filename, prompt_indices, host_url, server)
        return

    def construct_output_json(self, n, res_text):
        bs_id = self.bs_json[n]["accession"]
        res_text_json = extract_last_json(res_text)
        output_json = {}
        output_json["accession"] = bs_id
        if res_text_json == "":
            output_json["output"] = "Error: no json"
        else:
            output_json["output"] = json.loads(res_text_json)
        output_json["output_full"] = res_text

        ## add "characteristics" and "taxId"
        is_output_kv = False
        if isinstance(output_json["output"], dict):
            is_output_kv = True
        output_json["characteristics"] = {}
        if self.is_input_ebi_format and is_output_kv:
            for k, v in output_json["output"].items():
                output_json["characteristics"][k] = [{"text": v}]
            if "taxId" in self.bs_json[n]:
                output_json["taxId"] = self.bs_json[n]["taxId"]

        return output_json

    def ner(self, verbose=False, test=False):
        to = 10 if test else len(self.llm_input_json)
        base_messages = self.construct_messages()

        for i in range(0, to):
            input_bs = json.dumps(self.llm_input_json[i], indent=2)
            if i%10==0 and verbose and not test:
                print_time(str(i))

            messages = copy.deepcopy(base_messages)
            messages[-1]["content"] += input_bs
            options = {"temperature": 0}
            if self.server == "ollama":
                if self.host_url == "":
                    response = ollama.chat(model=self.model, messages=messages, options=options)
                else:
                    response = self.client.chat(model=self.model, messages=messages, options=options)
            else:
                response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0)
            res_text = response["message"]["content"]

            output_json = self.construct_output_json(i, res_text)

            print(json.dumps(output_json, sort_keys=True))
        return


class BsSelect(BsLlmProcess):
    def __init__(self, bs_json, model, prompt_filename, prompt_indices, host_url, metasra_tsv, llmner_json, server):
        super().__init__(bs_json, model, prompt_filename, prompt_indices, host_url, server)
        self.metasra_tsv = metasra_tsv
        # self.llmner_tsv = llmner_tsv
        # self.llmner_dict =  self.parse_llmner_tsv()
        self.llmner_json = llmner_json
        self.llmner_dict =  self.create_llmner_dict()
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
                    "output_full": spline[2].replace("  ", "\n ")
                }
        return llmner_dict

    def create_llmner_dict(self):
        llmner_dict = {}
        with open(self.llmner_json) as f:
            for line in f:
                sample = json.loads(line)
                llmner_dict[sample["accession"]] = {
                    "extracted_json": sample["output"],
                    "output_full": sample["output_full"]
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
        reformatted_dict["diseases"] = []
        for i in range(0, len(cvcl["xrefs"])):
            if cvcl["xrefs"][i].startswith("NCBI_TaxID:"):
                continue
            if cvcl["xrefs_comments"][i] != "":
                reformatted_dict["diseases"].append(cvcl["xrefs_comments"][i])

        subset_sex = [
            "Female",
            "Male",
            "Sex_unspecified",
            "Sex_ambiguous",
            "Mixed_sex",
        ]
        subset_type = [
            "Hybridoma",
            "Transformed_cell_line",
            "Cancer_cell_line",
            "Finite_cell_line",
            "Spontaneously_immortalized_cell_line",
            "Induced_pluripotent_stem_cell",
            "Telomerase_immortalized_cell_line",
            "Undefined_cell_line_type",
            "Hybrid_cell_line",
            "Embryonic_stem_cell",
            "Somatic_stem_cell",
            "Factor-dependent_cell_line",
            "Stromal_cell_line",
            "Conditionally_immortalized_cell_line",
        ]
        for subset in cvcl["subsets"]:
            if subset in subset_sex:
                if not "sex" in reformatted_dict:
                    reformatted_dict["sex"] = [subset]
                else:
                    reformatted_dict["sex"].append(subset)
            elif subset in subset_type:
                if not "cell line type" in reformatted_dict:
                    reformatted_dict["cell line type"] = [subset]
                else:
                    reformatted_dict["cell line type"].append(subset)
        return reformatted_dict

    def select(self, verbose=False, test=False):
        base_messages = self.construct_messages()
        print_time("Total samples for selection: " + str(len(self.bs_cvcl_cands)))

        for bs in self.bs_json:
            bs_id = bs["accession"]
            if bs_id not in self.bs_cvcl_cands:
                continue
            messages = copy.deepcopy(base_messages)

            ## Output from LLM in extraction
            messages.insert(-1, {
                "role": "assistant",
                "content": self.llmner_dict[bs_id]["output_full"]
            })

            ## Input of BioSample json
            messages[-2]["content"] += json.dumps(bs, indent=2)

            ## Candidate evaluation
            ### Replace "{{cell_line}}" in the prompt with this cell line name
            messages[-1]["content"] = messages[-1]["content"].replace("{{cell_line}}", str(self.llmner_dict[bs_id]["extracted_json"]["cell_line"]))
            ### Input of candidate terms
            for cvcl_cand in self.bs_cvcl_cands[bs_id]:
                cvcl_id = cvcl_cand["id"].replace(":", "_")
                messages[-1]["content"] += "\n```json: " + cvcl_id + ".json\n" + json.dumps(self.reformat_cvcl(cvcl_cand), indent=2) + "\n```\n"

            ## Ask LLM
            options = {"temperature": 0}
            if self.host_url == "":
                response = ollama.chat(model=self.model, messages=messages, options=options)
            else:
                response = self.client.chat(model=self.model, messages=messages, options=options)
            res_text = response["message"]["content"]

            ## json output
            res_text_json = extract_last_json(res_text)
            #print(bs_id, res_text_json.replace("\n", "").replace("\t", " "), res_text.replace("\n", " ").replace("\t", " "), sep="\t")
            output_json = {}
            output_json["accession"] = bs_id
            if res_text_json == "":
                output_json["output"] = "Error: no json"
            else:
                output_json["output"] = json.loads(res_text_json)
            output_json["output_full"] = res_text
            print(json.dumps(output_json, sort_keys=True))


        return
