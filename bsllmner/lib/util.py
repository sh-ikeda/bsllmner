import json
import datetime
import re
import sys


def load_json(json_filename):
    with open(json_filename, "r") as f:
        input_json = json.load(f)
    return input_json


def print_time(message=""):
    ct = datetime.datetime.now()
    print(f"[{ct}] {message}", file=sys.stderr)


def extract_last_json(text):
    json_candidates = re.findall(r'(\{.*?\}|\[.*?\])', text)

    if not json_candidates:
        return ""

    for candidate in reversed(json_candidates):
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            continue

    return ""
