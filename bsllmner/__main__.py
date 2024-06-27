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
    parser.add_argument('-y', '--prompt_types')
    parser.add_argument('-p', '--prompt_file')
    args = parser.parse_args()

    input_json = util.load_json(args.input_filename)
    verbose = args.verbose
    test = args.test
    model = args.model
    prompt_indices = args.prompt_indices.split(",")
    prompt_types = args.prompt_types.split(",")
    prompt_file = args.prompt_file
    util.print_time()
    ollama_chat.chat_ollama(input_json, model, prompt_indices, prompt_types, prompt_file, verbose, test)
    util.print_time()
    return


if __name__ == "__main__":
    main()
