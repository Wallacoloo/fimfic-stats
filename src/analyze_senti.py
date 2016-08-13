#!/usr/bin/env python3
"""Analyzes a text file and outputs information about character
associations to a json file
"""

import json, sys, warnings
from nltk import tokenize

from common import attribute_sentence_to_char, characters_plus_text

with warnings.catch_warnings():
    # The nltk.twitter library emits a completely irrelevant warning
    # about not having twython installed; silence that.
    warnings.simplefilter("ignore", UserWarning)
    from nltk.sentiment.vader import SentimentIntensityAnalyzer


sid = SentimentIntensityAnalyzer()

def analyze_senti(f):
    """Return a dict of information about the file f"""
    sentences = tokenize.sent_tokenize(f.read())

    sentiment = {}
    for c in characters_plus_text:
        sentiment[c] = {"raw": []}

    for s in sentences:
        if len(s) > 5000:
            # VADER seems to hang on exceptionally long sentences.
            # 5000 characters seems excessive for a single sentence,
            # and no doubt, it is. Thank "The Longest Trollfic Ever",
            # by "Troll": https://www.fimfiction.net/story/30328/the-longest-trollfic-ever
            print("Warning: sentence is > 5000 chars. Skipping: %s [...]" %s[:400])
            continue

        # Attribute the sentiment to a single character, if applicable
        # and remove all names
        c_in_s, s = attribute_sentence_to_char(s)

        compound = sid.polarity_scores(s)["compound"]
        # Track sentiment of the overall text
        sentiment["text"]["raw"].append(compound)

        if len(c_in_s) == 1:
            c, = c_in_s
            sentiment[c]["raw"].append(compound)

    # Compute average sentiments per character and entire text
    for p in sentiment.values():
        p["avg"] = sum(p["raw"])/len(p["raw"]) if p["raw"] else 0

    return dict(sentiment=sentiment)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <input txt file> <output json file>".format(sys.argv[0]))
    else:
        in_path, out_path = sys.argv[1:]
        in_file = open(in_path)
        out_dict = analyze_senti(in_file)
        out_file = open(out_path, "w")
        out_file.write(json.dumps(out_dict))
