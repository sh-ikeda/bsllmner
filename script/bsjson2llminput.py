import argparse
import json


def extract_text_to_tsv(input_json_filename, exception_json_filename=""):
    with open(input_json_filename, "r") as f:
        biosample_json = json.load(f)

    filter_keys = set()
    filter_values = set()
    if exception_json_filename != "":
        with open(exception_json_filename, "r") as f:
            exception_json = json.load(f)
        filter_keys |= set(exception_json["filter_keys"])
        # filter_values |= set(exception_json["filter_values"])

    output_list = []
    for entry in biosample_json:
        output_dict = {}
        output_dict["accession"] = entry["accession"]
        for k, v in entry["characteristics"].items():
            if (k not in filter_keys) and (not v[0]["text"] in filter_values):
                output_dict[k] = v[0]["text"]
        output_list.append(output_dict)
    print(json.dumps(output_list))
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='BioSample JSON file')
    parser.add_argument('-e', '--exception', default="", help='filter_key_val_rules.json of MetaSRA')
    args = parser.parse_args()
    input_json_filename = args.input
    exception_json_filename = args.exception
    extract_text_to_tsv(input_json_filename, exception_json_filename)


if __name__ == "__main__":
    main()
