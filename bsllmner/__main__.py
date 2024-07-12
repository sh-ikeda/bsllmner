import argparse
from .lib import util
from .lib import ollama_chat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename', help='BioSample JSON file')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-t', '--test', action='store_true')
    parser.add_argument('-m', '--model')
    parser.add_argument('-i', '--prompt_indices')
    args = parser.parse_args()

    input_json = util.load_json(args.input_filename)
    verbose = args.verbose
    test = args.test
    model = args.model
    prompt_indices = args.prompt_indices.split(",")
    util.print_time()
    ollama_chat.chat_ollama(input_json, model, prompt_indices, verbose, test)
    util.print_time()
    return


if __name__ == "__main__":
    main()
