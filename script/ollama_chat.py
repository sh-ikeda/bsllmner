import ollama
import sys
import json
import datetime
import argparse
import re


first_prompt = '''\
You are a smart curator of biological data.
You are given JSON-formatted data that describe a sample used in a biological experiment.
These data are written by scientists who conducted the experiment. Since they are not as familiar with data structurization as you, these might be not structurized well.
As a curator, extract some information described below from input data and output in JSON format.

These are information you must extract from input data:
1. tissue
   If a sample is considered to be a tissue section or a whole tissue, extract the tissue name from input and include it in output JSON with the "tissue" attribute. For example, if a sample is considered to be a section of liver, your output must include `"tissue": "liver"`.
2. host tissue
   Some biological samples are content of a tissue. For example, content of digestive tract can be used as a sample to investigate microbe of the tract.
   If a sample is considered to be content collected from a tissue, extract the tissue name from input and include it in output JSON with the "host_tissue" attribute. For example, if a sample is considered to be content collected from intestine, your output must include `"host_tissue": "intestine"`.
3. cell line
   A cell line is a group of cells that are genetically identical and have been cultured in a laboratory setting. For example, HeLa, Jurkat, HEK293, etc. are names of commonly used cell lines.
   If a sample is considered to be a cell line, extract the cell line name from input and include it in output JSON with the "cell_line" attribute. For example, if a sample is considered to be HeLa, your output must include `"cell_line": "HeLa"`.
   This attribute is supposed to describe a specific cell line name. Therefore, even if you find a string like "lung cancer cell line", you do not put the string in your output.
4. cell type
   If a sample is considered to be a specific type of cell, extract the cell type name from input and include it in output JSON with the "cell_type" attribute. For example, if a sample is considered to be leukocyte, your output must include `"cell_type": "leukocyte"`.
   Note that some samples might be experienced or experiencing cell differentiation. In this case, "cell_type" attribute is supposed to be a name of resulting differentiated cell, rather than a name of a cell the sample derived from. For example, if a sample is considered to be neuron differentiated from iPS cells, your output must include `"cell_type": "neuron"`, rather than `"cell_type": "iPS cells"`.
5. disease
   If input data mention a disease of the organism the sample derived, extract the disease name from input and include it in output JSON with the "disease" attribute. For example, if a sample is considered to be collected from a patient of amyotrophic lateral sclerosis, your output must include `"disease": "amyotrophic lateral sclerosis"`.

Your output is a JSON-formatted data including all data you extracted. If you do not find information listed above in input data, you do not output the attribute. For example, if a sample is considered to be neuron collected from a patient of amyotrophic lateral sclerosis, your output is: {"cell_type": "neuron", "disease": "amyotrophic lateral sclerosis"}.

Are you ready?'''

examples = [
    '''{
    "accession": "SAMEA14090969",
    "age": "70",
    "broker name": "ArrayExpress",
    "cell_type": "memory B cell",
    "common name": "human",
    "description": "Protocols: All spleen in this study were collected from organ donors who died from stroke or head trauma. None of them had lymphoma or autoimmune disease. Immediately after splenectomy, mononuclear cells were isolated from crushed pieces of splenic tissue by ficoll density-gradient centrifugation and stored in liquid nitrogen. After thawing, mononuclear cells were counted and stained with antibodies directed against surface markers. CD21hiCD20hi (CD21high IgG+ memory B cell) and CD21intCD20int memory B cell subsets (CD21int IgG+ memory B cell) were then bulk FACS-sorted (AriaIII) from gated IgG+ switched memory B cells (IgG+CD27+CD20+IgD-) in parallel with naives B cells (CD20+CD38lowCD24intCD27-IgD+CD3-CD14-CD16+). Assay for Transposase-Accessible Chromatin with high-throughput sequencing (ATAC-seq) was performed on 50000 cells of each sorted population according to published methods (Buenrostro, Nature Methods, 2013, PMID: 24097267). Libraries were amplified and prepared according to published methods (Buenrostro, Nature Methods, 2013, PMID: 24097267).",
    "developmental stage": "adult",
    "disease": "normal",
    "immunophenotype": "CD21high IgG+",
    "individual": "HD38",
    "organism": "Homo sapiens",
    "organism part": "spleen",
    "sex": "female",
    "title": "Sample 1"
  } ''',
    '''  {
    "accession": "SAMEA103885158",
    "age": "40-44",
    "cell type": "iPSC derived cell line",
    "description": "Macrophages derived from induced pluripotent stem cell HPSI1113i-bima_1 day 35 after start of differentiation, treated with interferon gamma.",
    "differentiation start date": "2014/11/07",
    "disease state": "normal",
    "ethnicity": "White - White British",
    "material": "cell line",
    "organism": "Homo sapiens",
    "sampling date": "2014/12/12",
    "sex": "male",
    "target cell type": "macrophage",
    "time point": "day 35",
    "treatment": "interferon gamma"
  } ''',
    '''  {
    "accession": "SAMN32011038",
    "Sex": "male",
    "cell type": "oligodendrocyte lineage cells (NeuN-SOX10+)",
    "chip antibody": "H3K27ac (Active Motif #39133)",
    "disease": "C9-ALS",
    "donor id": "A10",
    "genotype": "C9ORF72+",
    "organism": "Homo sapiens",
    "source_name": "motor cortex",
    "tissue": "motor cortex",
    "title": "ChIP-seq H3K27ac, C9-ALS donor A10, Motor cortex, Oligodendrocyte lineage cells"
    }''',
    '''  {
    "accession": "SAMD00004141",
    "organism": "Homo sapiens",
    "sample comment": "Hela cells which were cultured in Dulbecco's modified Eagle's medium (DMEM) supplemented with 10% fetal bovine serum under a humidified atmosphere with 5% CO2 at 37Â°C.",
    "sample name": "DRS000576",
    "title": "Hela_Ser2P/Ser5P/Ser7P-RNAP2_ChIPSeq"
  }'''
]

answers = [
    '{"cell_type": "memory B cell", "tissue": "spleen"}',
    '{"cell_type": "macrophage"}',
    '{"cell_type": "oligodendrocyte", "tissue": "motor cortex", "disease": "C9-ALS"}',
    '{"cell_line": "Hela"}'
]


def chat_ollama(input_json, model, verbose=False, test=False):
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
        # print(bs_id, res_text.replace("\n", " "), sep="\t")
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
    args = parser.parse_args()

    input_json = load_json(args.input_filename)
    verbose = args.verbose
    test = args.test
    model = args.model
    print_time()
    chat_ollama(input_json, model, verbose, test)
    print_time()
    return


if __name__ == "__main__":
    main()
