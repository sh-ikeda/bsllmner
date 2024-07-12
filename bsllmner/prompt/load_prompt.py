import sys
import re
import os


fname = "prompt.md"
dirname = os.path.dirname(os.path.abspath(__file__))


def parse_md():
    dic = {}
    with open(dirname + "/" + fname, "r") as f:
        current_id = ""
        is_first_line = False
        for line in f:
            if line[0] == "#":
                current_id = re.sub("^# ", "", line).strip()
                dic[current_id] = {}
                dic[current_id]["text"] = ""
                is_first_line = True
            elif is_first_line:
                dic[current_id]["role"] = line.strip()
                is_first_line = False
            elif current_id != "":
                dic[current_id]["text"] += line
    return dic


def main():
    print(parse_md(), file=sys.stderr)


if __name__ == "__main__":
    main()
