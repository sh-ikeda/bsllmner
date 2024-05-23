import json
import datetime
import sys


def load_json(json_filename):
    with open(json_filename, "r") as f:
        input_json = json.load(f)
    return input_json


def print_time(message=""):
    ct = datetime.datetime.now()
    print(f"[{ct}] {message}\n", file=sys.stderr)
