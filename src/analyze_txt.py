#!/usr/bin/env python
"""Analyzes a text file and outputs information about character
associations to a json file
"""

import json, re, sys
from nltk.corpus import sentiwordnet as swn
# Sentence boundary occurs as punctuation (. ! ?) followed by at least
# one space, followed by a capital letter. Note that double-qoutes in
# in this region should be accepted (entering or leaving a quote).
sentence_boundary = re.compile(r'(?<=[.!?])"?\s+"?(?=[A-Z])', re.M)
word_boundary = re.compile(r'\s')
valid_word_chars = "-_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

characters = ["Applejack", "Fluttershy", "Pinkie Pie", "Rainbow Dash", "Rarity", "Twilight Sparkle"]

def rank_sentiment(s):
    """Return how 'positive' a sentence is.
    This is done using data from SentiWordNet, which ranks words based
    on their: positivity, negativity and objectivity.
    """
    # nltk SentiWordNet example: http://www.nltk.org/howto/sentiwordnet.html
    rank = 0
    for word_raw in re.split(word_boundary, s):
        word = "".join(c for c in word_raw if c in valid_word_chars)
        # each word can match multiple (or 0) uses
        matches = list(swn.senti_synsets(word))
        if matches: # avoid div-by-0
            rank += sum(m.pos_score() - m.neg_score() for m in matches)/len(matches)
    return rank

def analyze(f):
    """Return a dict of information about the file f"""
    sentences = re.split(sentence_boundary, f.read())
    print(sentences)

    sentiment = {}
    for c in characters:
        sentiment[c] = {"raw": []}

    for s in sentences:
        c_in_s = [c for c in characters if c in s]
        if len(c_in_s) == 1:
            # If the sentence contains multiple names, it would be very
            # easy to attribute the opinion to the wrong character.
            c = c_in_s[0]
            sentiment[c]["raw"].append(rank_sentiment(s.replace(c, "")))

    for p in sentiment.values():
        p["avg"] = sum(p["raw"])/len(p["raw"]) if p["raw"] else 0

    return dict(sentiment=sentiment)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <input txt file> <output json file>".format(sys.argv[0]))
    else:
        in_path, out_path = sys.argv[1:]
        in_file = open(in_path)
        out_dict = analyze(in_file)
        out_file = open(out_path, "w")
        out_file.write(json.dumps(out_dict))
