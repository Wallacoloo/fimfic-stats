#!/usr/bin/env python
# Analyzes a text file and outputs information about character
# associations to a json file

import json, re, sys
# Sentence boundary occurs as punctuation (. ! ?) followed by at least
# one space, followed by a capital letter. Note that double-qoutes in
# in this region should be accepted (entering or leaving a quote).
sentence_boundary = re.compile(r'(?<=[.!?])"?\s+"?(?=[A-Z])', re.M)

def analyze(f):
    """Return a dict of information about the file f"""
    sentences = re.split(sentence_boundary, f.read())
    print(sentences)
    # TODO: implement
    return {}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <input txt file> <output json file>".format(sys.argv[0]))
    else:
        in_path, out_path = sys.argv[1:]
        in_file = open(in_path)
        out_dict = analyze(in_file)
        out_file = open(out_path, "w")
        out_file.write(json.dumps(out_dict))
