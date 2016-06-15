#!/usr/bin/env python
"""Analyzes a text file and outputs information about character
associations to a json file
"""

import json, sys, warnings
from nltk import tokenize

from common import characters

with warnings.catch_warnings():
    # The nltk.twitter library emits a completely irrelevant warning
    # about not having twython installed; silence that.
    warnings.simplefilter("ignore", UserWarning)
    from nltk.sentiment.vader import SentimentIntensityAnalyzer


sid = SentimentIntensityAnalyzer()

def analyze(f):
    """Return a dict of information about the file f"""
    sentences = tokenize.sent_tokenize(f.read())

    sentiment = {}
    for c in characters:
        sentiment[c] = {"raw": []}

    for s in sentences:
        # Try to assign the sentiment to a SINGLE character
        c_in_s = {}
        for c, nicks in characters.items():
            for nick in nicks:
                if nick in s:
                    c_in_s[c] = nick
                    break

        # Replace all character names with a neutral word
        # sum() is used to flatten the dict items
        for nick in c_in_s.values():
            s = s.replace(nick, "it")

        if len(s) > 5000:
            # VADER seems to hang on exceptionally long sentences.
            # 5000 characters seems excessive for a single sentence,
            # and no doubt, it is. Thank "The Longest Trollfic Ever",
            # by "Troll": https://www.fimfiction.net/story/30328/the-longest-trollfic-ever
            print("Warning: sentence is > 5000 chars. Skipping: %s [...]" %s[:400])
            break

        compound = sid.polarity_scores(s)["compound"]
        # Track sentiment of the overall text
        sentiment["text"]["raw"].append(compound)

        # Attribute the sentiment to a single character, if applicable
        if len(c_in_s) == 1:
            c, = c_in_s.keys()
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
