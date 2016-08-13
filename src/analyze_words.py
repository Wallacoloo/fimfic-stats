#!/usr/bin/env python3
"""Analyzes the words associated with each character
"""

import json, sys
from nltk import tokenize

from common import attribute_sentence_to_char, characters_plus_text

def analyze_words(f):
    """Returns a dict of word-association information extracted from
    the file f.
    """
    # associations is structured as:
    # { "char_name":
    #   { "word": 123,
    #     "word2": 7,
    #   }
    # }
    associations = {}
    # char_pairs is structured as:
    # { "character1,character2": 3,
    #   "character1,character3,character4": 8
    # }
    # where "character1,character2" are the names of the characters,
    # sorted alphabetically and joined with a comma
    char_pairs = {}
    for c in characters_plus_text:
        associations[c] = {}

    sentences = tokenize.sent_tokenize(f.read())
    for s_ in sentences:
        c_in_s, s = attribute_sentence_to_char(s_)
        pair_name = ",".join(sorted(c_in_s))

        # Increment the number of times this pair has been seen
        char_pairs[pair_name] = char_pairs.get(pair_name, 0) + 1

        # Parser will default to splitting words on apostrophe - fight that.
        # Note: it also turns end-quotes (") into "''" and start-quotes (") into "``"
        # We don't care about that - only the actual words
        words = tokenize.word_tokenize(s.lower().replace("'", '`'))
        words_fixed = []
        for w in words:
            # Undo the contraction hack
            w = w.replace("`", "'")
            # Remove extra punctuation
            w = "".join(l for l in w if l in "abcdefghijklmnopqrstuvwxyz-'")
            w = w.strip("'").strip("-").strip("'")
            if w: words_fixed.append(w)
        
        for c in tuple(c_in_s) + ("text",):
            for word in words_fixed:
                # Increment the number of times this word has been seen
                associations[c][word] = associations[c].get(word, 0) + 1
            
    return dict(associations=associations, char_pairs=char_pairs)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <input txt file> <output json file>".format(sys.argv[0]))
    else:
        in_path, out_path = sys.argv[1:]
        in_file = open(in_path)
        out_dict = analyze_words(in_file)
        out_file = open(out_path, "w")
        out_file.write(json.dumps(out_dict))
