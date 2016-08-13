#!/usr/bin/env python3
"""Produce various text-only data of interest, e.g. word frequencies.
"""

import json, sys

def word_frequencies(agg):
    """Across the entire text, create a dict that maps word -> frequency (float)
    """
    # These map word -> count
    words = agg["associations"]["text"]
    num_words = sum(words.values())
    freqs = {}
    for k, v in words.items():
        freq = v/num_words
        # Safely ignore the very rare typos.
        # Currently, a word occuring only once has f = 4e-9
        if freq > 5e-8:
            freqs[k] = freq
    return freqs

text_functions = {
    "word_frequencies.json": word_frequencies,
}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <aggregated.json> <target_name>".format(sys.argv[0]))
    else:
        aggregated_path, target_name = sys.argv[1:]
        agg = json.loads(open(aggregated_path, "r").read())

        func = text_functions[target_name]
        data = func(agg)
        print(json.dumps(data))
