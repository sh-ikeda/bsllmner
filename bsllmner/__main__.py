import argparse
from .lib import util
from .lib import ollama_chat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=["extract", "review"])
    parser.add_argument('input_filename', help='BioSample JSON file')
    parser.add_argument('-r', '--metasra_tsv', help='MetaSRA output tsv file. Required for review mode.')
    parser.add_argument('-l', '--llmner_tsv', help='Extraction output tsv file. Required for review mode.')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-m', '--model')
    parser.add_argument('-p', '--prompt_filename', default="")
    parser.add_argument('-i', '--prompt_indices')
    parser.add_argument('-u', '--host_url', default="")
    args = parser.parse_args()

    mode = args.mode
    input_json = util.load_json(args.input_filename)
    metasra_tsv = args.metasra_tsv
    llmner_tsv = args.llmner_tsv
    verbose = args.verbose
    test = args.test
    model = args.model
    prompt_filename = args.prompt_filename
    prompt_indices = args.prompt_indices.split(",")
    host_url = args.host_url
    util.print_time()

    if mode == "extract":
        bsner = ollama_chat.BsNer(input_json, model, prompt_filename, prompt_indices, host_url)
        bsner.ner(verbose, test)
    elif mode == "review":
        bsreview = ollama_chat.BsReview(input_json, model, prompt_filename, prompt_indices, host_url, metasra_tsv, llmner_tsv)
        bsreview.review(verbose, test)
    util.print_time()
    return


if __name__ == "__main__":
    main()
