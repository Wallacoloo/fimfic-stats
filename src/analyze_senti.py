#!/usr/bin/env python
"""Analyzes a text file and outputs information about character
associations to a json file
"""

import json, sys, warnings
from nltk import tokenize
with warnings.catch_warnings():
    # The nltk.twitter library emits a completely irrelevant warning
    # about not having twython installed; silence that.
    warnings.simplefilter("ignore", UserWarning)
    from nltk.sentiment.vader import SentimentIntensityAnalyzer

# There is some bias here based on which characters I consider important
# enough to track. My intention is mainly to analyze the main 6, though
# and beyond that most of this data is probably not going to be used
# anyway.
characters = {
        # Main 6 + Spike
        "Applejack": ("Applejack",),
        "Fluttershy": ("Fluttershy",),
        "Pinkie Pie": ("Pinkie Pie", "Pinkie",),
        "Rainbow Dash": ("Rainbow Dash", "Rainbow", "Dash",),
        "Rarity": ("Rarity",),
        "Twilight Sparkle": ("Twilight Sparkle", "Twilight", "Sparkle",),
        "Spike": ("Spike",),
        # CMC
        "Apple Bloom": ("Apple Bloom",),
        "Scootaloo": ("Scootaloo",),
        "Sweetie Belle": ("Sweetie Belle", "Sweetie",),
        "Babs Seed": ("Babs Seed", "Babs",),
        # Royalty
        # 'Princess' and 'Principal' have no sentiment in VADER, so we
        # don't have to worry about those titles
        "Celestia": ("Celestia",),
        "Luna": ("Luna",),
        "Cadance": ("Cadance",),
        "Shining Armor": ("Shining Armor", "Shining",),
        "Flurry Heart": ("Flurry Heart",),
        # Recurring Villains (possibly reformed)
        "Nightmare Moon": ("Nightmare Moon",),
        "Discord": ("Discord",),
        "Gilda": ("Gilda",),
        # Trixie is VERY commonly associated with 'great' and 'powerful',
        # but at least remove these words when used as a title
        "Trixie": ("Great and Powerful Trixie",
            "Great And Powerful Trixie", "great and powerful Trixie",
            "Trixie",),
        # These characters often appear by their nicknames, but their
        # nicknames are easily confused with nouns when occuring at the
        # start of a sentence
        #"Sunset Shimmer": ("Sunset Shimmer", "Sunset"),
        #"Starlight Glimmer": ("Starlight Glimmer", "Starlight"),
        # hack to track the sentiment of the overall text
        "text": (),
}

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
