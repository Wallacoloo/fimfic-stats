#!/usr/bin/env python
"""Analyzes a text file and outputs information about character
associations to a json file
"""

import json, sys
from nltk import tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

characters = ("Applejack", "Fluttershy", "Pinkie Pie", "Rainbow Dash", "Rarity", "Twilight Sparkle")

sid = SentimentIntensityAnalyzer()

def analyze(f):
    """Return a dict of information about the file f"""
    sentences = tokenize.sent_tokenize(f.read())
    print(sentences)

    sentiment = {}
    for c in characters + ("text",):
        sentiment[c] = {"raw": []}

    for s in sentences:
        compound = sid.polarity_scores(s)["compound"]
        # Track sentiment of the overall text
        sentiment["text"]["raw"].append(compound)
        # Try to assign the sentiment to a SINGLE character
        c_in_s = [c for c in characters if c in s]
        if len(c_in_s) == 1:
            c = c_in_s[0]
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
        out_dict = analyze(in_file)
        out_file = open(out_path, "w")
        out_file.write(json.dumps(out_dict))
