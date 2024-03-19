import sys
import re
import os


fname = "prompt.md"
dirname = os.path.dirname(os.path.abspath(__file__))


def parse_md():
    dic = {}
    with open(dirname + "/" + fname, "r") as f:
        current_id = ""
        for line in f:
            if line[0] == "#":
                current_id = re.sub("^# ", "", line).strip()
                dic[current_id] = ""
            elif current_id != "":
                dic[current_id] += line
    return dic


def main():
    print(parse_md(), file=sys.stderr)


if __name__ == "__main__":
    main()
