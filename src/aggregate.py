#!/usr/bin/env python3
"""Take precompiled statistics of each indivual story and draw
conclusions of the entire set, or on individual authors, etc.
"""

import json, os, sys

from common import characters_plus_text, story_length

def average(data):
    s = 0
    n = 0
    for i in data:
        s += i
        n += 1
    return s/max(n, 1)

def files_of_type(srcdir, ext):
    for root, dirs, files in os.walk(srcdir):
        for f in files:
            if f.endswith(ext):
                yield os.path.join(root, f)

def avg_data_at_percent(data, percent):
    """Given an array of numbers, return the average value at any percent in the data.
    0 and 100 (percent) are inclusive. This is done by making the first
    and last percent on half-length.
    """
    idx_start = max(0, int((percent-0.5)*len(data)/100))
    idx_end = min(len(data), int((percent+0.5)*len(data)/100))
    idx_end = max(idx_start+1, idx_end) # need at least one sample.
    return average(data[idx_start:idx_end])

def aggregate(index, src_paths):
    """Perform several analyses on the .json results in src_paths.
    """
    results = {}
    sentiment = {}
    # Number of times each character is mentioned by name
    char_mentions = {}
    associations = {}
    # "char1,char2": {"in_a_sentence": <int>, "in_a_story": <int>}
    char_pairs = {}
    results["sentiment"] = sentiment
    results["story_lengths"] = []
    results["char_mentions"] = char_mentions
    results["associations"] = associations
    results["char_pairs"] = char_pairs
    for c in tuple(characters_plus_text.keys()):
        # Each month contains a sum of sentiment and a count of sentiments
        # which can be used to derive the average
        sentiment[c] = {
            # average sentence sentiment by month since Jan 2010
            "months": [ {"sum": 0, "count": 0} for i in range(100)],
            # Average sentence sentiment at any point through a story.
            "storyarc_percent": [ {"sum": 0, "count": 0} for i in range(101)],
            # Short-format (<= N sentences), medium, long-format stories
            "storyarc_percent_short": [ {"sum": 0, "count": 0} for i in range(101)],
            "storyarc_percent_med": [ {"sum": 0, "count": 0} for i in range(101)],
            "storyarc_percent_long": [ {"sum": 0, "count": 0} for i in range(101)],
        }
        char_mentions[c] = {
            "in_a_sentence": 0,
            # Count of # of stories the character appears (redundant)
            "in_a_story": 0,
            # map story_id -> # of sentences in which char appears
            "in_stories": {},
        }
        # "word": <int>
        associations[c] = {}

    for srcno, p_senti in enumerate(src_paths):
        if srcno % 10000 == 0: print('story:', srcno)
        # Special thanks to this story by Sharp Spark for having not
        # a single English character in his title, making parsing the
        # id excessively complicated: https://www.fimfiction.net/story/269475
        story_id = p_senti.split("/")[-1].replace(".sentiment.json","").split("-")[-1]
        story_meta = index[story_id]
        datum_senti = json.loads(open(p_senti, "r").read())
        p_words = p_senti.replace(".sentiment.json", ".words.json")
        datum_words = json.loads(open(p_words, "r").read())

        num_sentences = len(datum_senti["sentiment"]["text"]["raw"])
        # Sentiment data is unavailable on a per-chapter basis, so
        # we generalize them to the average publication date.
        avg_pub_date = average(ch["date_modified"] for ch in story_meta["chapters"])
        # number of months since 2010
        pub_month = int(12*(avg_pub_date / (60*60*24*365.25) - 40))

        results["story_lengths"].append(num_sentences)

        # aggregate the sentiments
        for c in tuple(characters_plus_text.keys()):
            senti = datum_senti["sentiment"][c]["raw"]
            if senti:
                # The character's score would default to 0 if
                # the character flat-out doesn't ever appear in
                # the story; although this is OK for most measurements,
                # it would incorrectly drag down the character's
                # portrayal based on percentage into the story
                # (sentiment[c]["storyarc_percent_x"])
                sentiment[c]["months"][pub_month]["sum"] += sum(senti)
                sentiment[c]["months"][pub_month]["count"] += len(senti)

                char_mentions[c]["in_a_sentence"] += len(senti)
                char_mentions[c]["in_a_story"] += bool(senti)
                char_mentions[c]["in_stories"][story_id] = len(senti)

                # Determine which storyarc sets this story applies to
                apropo_sets = [sentiment[c]["storyarc_percent"]]
                if num_sentences <= story_length.short:
                    apropo_sets.append(sentiment[c]["storyarc_percent_short"])
                elif num_sentences <= story_length.med:
                    apropo_sets.append(sentiment[c]["storyarc_percent_med"])
                else:
                    apropo_sets.append(sentiment[c]["storyarc_percent_long"])

                for percent in range(101):
                    arc_senti = avg_data_at_percent(senti, percent)
                    for arcs in apropo_sets:
                        arcs[percent]["sum"] += arc_senti
                        arcs[percent]["count"] += 1

        # Aggregate the character pairs
        for char_pair, count in datum_words["char_pairs"].items():
            it = char_pairs.get(char_pair,
                dict(in_a_story=0, in_a_sentence=0, in_stories={}))
            it["in_a_sentence"] += count
            it["in_a_story"] += 1
            it["in_stories"][story_id] = count
            char_pairs[char_pair] = it

        # Aggregate the word associations
        for char in characters_plus_text:
            for word in datum_words["associations"][char]:
                num_seen = associations[char].get(word, 0)
                associations[char][word] = num_seen + 1


    return results


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: {} <index> <source dir> <output json file>".format(sys.argv[0]))
    else:
        index_path, in_dir, out_path = sys.argv[1:]
        index = json.loads(open(index_path, "r").read())
        in_files = files_of_type(in_dir, ".sentiment.json")
        out_dict = aggregate(index, in_files)
        out_file = open(out_path, "w")
        out_file.write(json.dumps(out_dict))
