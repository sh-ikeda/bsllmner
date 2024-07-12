# 1
user
You are a smart curator of biological data.
You are given JSON-formatted data that describe a sample used in a biological experiment.
These data are written by scientists who conducted the experiment. Since they are not as familiar with data structurization as you, these might be not structurized well.
As a curator, extract information described below from input data and output in JSON format.

Follow the steps below to construct your output JSON.
1. Extract tissue
   If a sample is considered to be a tissue section or a whole tissue, extract the tissue name from input and include it in output JSON with the "tissue" attribute. For example, if a sample is considered to be a section of liver, your output must include `"tissue": "liver"`.
2. Extract host tissue
   Some biological samples are content of a tissue. For example, content of digestive tract can be used as a sample to investigate microbe of the tract. If a sample is considered to be content collected from a tissue, extract the tissue name from input and include it in output JSON with the "host_tissue" attribute. For example, if a sample is considered to be content collected from intestine, your output must include `"host_tissue": "intestine"`.
3. Check differentiation
   If a sample is considered to have experienced cell differentiation, extract the cell type name which the sample derived from and include it in output JSON with the "differentiated_from" attribute. Also, extract the cell type name which the sample differentiated into and include it in output JSON with the "differentiated_into" attribute. For example, if a sample is considered to be neuron differentiated from iPS cells, your output must include `"differentiated_from": "iPS cells"` and `"differentiated_into": "neuron"`.
   If you extract a cell name in this step, then proceed to the step 6. Otherwise, proceed to the step 4.
4. Extract cell line
   A cell line is a group of cells that are genetically identical and have been cultured in a laboratory setting. For example, HeLa, Jurkat, HEK293, etc. are names of commonly used cell lines.
   If a sample is considered to be a cell line, extract the cell line name from input and include it in output JSON with the "cell_line" attribute. For example, if a sample is considered to be HeLa, your output must include `"cell_line": "HeLa"`.
   This attribute is supposed to describe a specific cell line name. Therefore, even if you find a string like "lung cancer cell line", you do not put the string in your output.
5. Extract cell type
   If a sample is considered to be a specific type of cell, extract the cell type name from input and include it in output JSON with the "cell_type" attribute. For example, if a sample is considered to be leukocyte, your output must include `"cell_type": "leukocyte"`.
6. Extract disease
   If input data mention a disease of the organism the sample derived, extract the disease name from input and include it in output JSON with the "disease" attribute. For example, if a sample is considered to be collected from a patient of amyotrophic lateral sclerosis, your output must include `"disease": "amyotrophic lateral sclerosis"`.
7. Output JSON
   Your final output is a JSON-formatted data including all data you extracted. If you do not find information listed above in input data, you do not output the attribute. For example, if a sample is considered to be neuron collected from a patient of amyotrophic lateral sclerosis, your output is: {"cell_type": "neuron", "disease": "amyotrophic lateral sclerosis"}.

Are you ready?
# 2
user
A cell line is a group of cells that are genetically identical and have been cultured in a laboratory setting. For example, HeLa, Jurkat, HEK293, etc. are names of commonly used cell lines.

I will input json formatted metadata of a sample for a biological experiment. If the sample is considered to be a cell line, extract the cell line name from the input data.

Your output must be JSON format, like {"cell_line": "NAME"} .
"NAME" is just a place holder. Replace this with a string you extract.

When input sample data is not of a cell line, you are not supposed to extract any text from input.
If you can not find a cell line name in input, your output is like {"cell_line": "None"} .
Are you ready?

# 3
user
I will input json formatted metadata of a sample for a biological experiment. If the sample is considered to be a tissue section or a whole tissue, extract the tissue name from the input data.
Your output must be JSON format, like {"tissue": "NAME"} .
"NAME" is just a place holder. Replace this with a string you extract.
For example, if a sample is considered to be a section of liver, your output is {"tissue": "liver"}.
When input sample data is not considered to be a tissue section or a whole tissue, you are not supposed to extract any text from input. In such a case, your output is like {"tissue": "None"} .
Are you ready?

# 4
user
A gene knockout (KO), also known as a gene deletion, involves completely eliminating the expression of a target gene by replacing it with a non-functional version, usually through homologous recombination in cells or animals. This results in a complete loss of the gene's function.

Meanwhile, a gene knockdown (KD), also known as RNA interference (RNAi), involves reducing the expression of a target gene without completely eliminating it. KD is achieved by introducing small RNA molecules, siRNA or shRNA, that specifically bind to and degrade the messenger RNA (mRNA) of the target gene.

I will input json formatted metadata of a sample for a biological experiment. If the sample is considered to be had a gene knocked-out or knocked-down, extract the gene name from the input data.

Your output must be JSON format, like {"knockout": "NAME", "knockdown": "NAME"} .
"NAME" is just a place holder. Replace this with the string you extract.
When input sample data is not considered to be had a gene knocked-out or knocked-down, the value of "knockout" or "knockdown" of your output JSON must be "None".
Are you ready?

# 5
system
You are a smart curator of biological data

# 6
assistant
I'm ready! Please provide the JSON formatted metadata of the sample for the biological experiment.

# 7
user
Then think step by step for the data below.
