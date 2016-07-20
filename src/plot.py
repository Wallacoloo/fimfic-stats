#!/usr/bin/python
"""Plots the various aggregated data
"""

import datetime, inspect, json, os.path, random, sys
from math import ceil, cos, floor, pi, tan
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import enchant

from common import characters, main6, story_length

# Based on http://helmet.kafuka.org/ponycolors/
colors = {
    "Applejack": "#FCBA63",
    "Fluttershy": "#F0DA75",
    "Pinkie Pie": "#F6B7D2",
    "Rainbow Dash": "#9EDBF8",
    "Rarity": "#BEC2C3",
    "Twilight Sparkle": "#D19FE4",

    "Spike": "#51C456",
    "Apple Bloom": "#F74160",
    "Scootaloo": "#F37033",
    "Sweetie Belle": "#B28DC0",
    "Babs Seed": "#A9541B",
    "Celestia": "#FFD791",
    "Luna": "#2E4883",
    "Cadance": "#FFCCE6",

    "Shining Armor": "#355397",
    "Flurry Heart": "#00ADA8",

    "Nightmare Moon": "#140A2E",
    "Discord": "#E3AE81",
    "Gilda": "#AA7053",
    "Trixie": "#71B8EF",

    "text": "#101010",
}

# Words that are used as common-speech in canon
fim_words = set([
    "alicorn",
    "alicorns",
    "anypony",
    "canterlot",
    "draconequus",
    "everypony",
    "equestria",
    "fillydelphia",
    "manehattan",
    "manticore",
    "nopony",
    "pegasi",
    "ponyville",
    "somepony",
])

legendFont = FontProperties()
legendFont.set_size('small')

cot = lambda x: 1/tan(x)
mean = lambda x: sum(x)/len(x)
floorto = lambda x, ival: floor(x/ival)*ival
ceilto = lambda x, ival: ceil(x/ival)*ival

def story_rating(story_info, thresh=1):
    """Return (valid, rating) where valid indicates if the story has
    enough likes/dislikes for the rating to be valid, rating is
    (L-D)/(L+D), where L=likes, D=dislikes
    """
    L, D = story_info["likes"], story_info["dislikes"]
    valid = L+D >= thresh
    rating = (L-D)/max(1, L+D)
    return valid, rating

def smooth(month_data=None, percent_data=None):
    """Smooth month-based data so that the long-term trends are more visible
    """
    # Work based on http://www.claysturner.com/dsp/Butterworth%20Filter%20Formulae.pdf
    # data is sampled by months, want trends > 6 months to be visible
    # Use fc =~ 1/6
    if month_data is not None:
        fc = 1/12
    if percent_data is not None:
        fc = 1/25
    c = cot(pi*fc)
    # Second order LPF butterworth:
    alpha = 2*cos(pi/4)
    # Coefficients (listed at the very bottom of the PDF)
    DC = 1/(1+c*(c+alpha))
    # x and y coefficients for filtering
    xk = [1, 2, 1]
    yk = [1, 2*(1-c*c)/(1+c*(c+alpha)), (1+c*(c-alpha))/(1+c*(c+alpha))]
    # Our filter is:
    # yk[0] y[n-0] + yk[1] y[n-1] + ... = DC(xk[0]x[n-0] + xk[1]x[n-1] + ... )
    def filt(x, y, n):
        # Follow the equation further up to solve for y[n-0]
        # When indexing x[n-k], y[n-k] for n-k < 0, we assume a
        # steady-state value for n-k <= 0
        if n == 0:
            return x[0]

        rhs = DC*sum(x[max(0, n-k)] * xk[k] for k in range(3))
        other_y = sum(y[max(0, n-k)] * yk[k] for k in range(1, 3))
        this_y = (rhs - other_y) / yk[0]
        return this_y

    x = month_data or percent_data
    y = []
    for n in range(len(x)):
        y.append(filt(x, y, n))

    return y


def char_senti_by_month(agg, chars=main6, do_smooth=False, ylim=(0.00, 0.13)):
    """Create a plot displaying typical character sentiment
    on fimfiction vs time.
    """
    # Prepare data
    pdata = {}
    for char in chars:
        monthdata = agg["sentiment"][char]["months"]
        startidx = min(i for i in range(100) if monthdata[i]["count"])
        lastidx = max(i for i in range(100) if monthdata[i]["count"])
        xdata = [datetime.datetime(year=2010+int(i/12), month=i%12+1, day=1) for i in range(startidx, lastidx+1)]
        ydata = [month["sum"]/max(1, month["count"]) for month in agg["sentiment"][char]["months"][startidx:lastidx+1] ]
        if do_smooth:
            ydata = smooth(month_data=ydata)
        pdata[char] = [xdata, ydata]

    # Plot data
    for char, cdata in pdata.items():
        plt.plot_date(cdata[0], cdata[1], '-', label=char, color=colors[char], lw=2.5)

    # Labels
    plt.xlabel("Year")
    plt.ylabel("Average compound sentiment")
    title_pre = "Full-text" if chars == ("text",) else "Character"
    title_post = " (smoothed)" if do_smooth else ""
    plt.title(title_pre + " sentiment vs. time" + title_post)

    if ylim: plt.ylim(*ylim)
    if len(pdata) > 1:
        plt.legend(loc="best", prop=legendFont, ncol=1+len(chars)//12)

def text_senti_by_storyarc(agg, chars=("text",), do_smooth=False, arcs=("",)):
    """Plot the sentiment of the average story at any percentage through
    that story
    """

    storyarc_length_map = dict(
        _short="<{} sentences".format(story_length.short),
        _med="{}-{} sentences".format(story_length.short+1, story_length.med),
        _long=">{} sentences".format(story_length.med)
    )

    # Prepare data
    pdata = {}
    for char in chars:
        for arc in arcs:
            percdata = agg["sentiment"][char]["storyarc_percent" + arc]
            xdata = range(101)
            ydata = [percent["sum"]/max(1, percent["count"]) for percent in percdata ]
            if do_smooth:
                ydata = smooth(percent_data=ydata)
            if len(arcs) == 1:
                lbl = char
            elif len(chars) == 1:
                lbl = storyarc_length_map[arc]
            else:
                # Have multiple characters AND bins
                lbl = "{} ({})".format(char, storyarc_length_map[arc])

            pdata[lbl] = [xdata, ydata]

    # Plot data
    for char, cdata in pdata.items():
        plt.plot(cdata[0], cdata[1], '-', label=char, color=colors.get(char, None), lw=2.5)

    # Labels
    plt.xlabel("Percent into story")
    plt.ylabel("Average compound sentiment")
    title_pre = "Sentence" if chars == ("text",) else "Character"
    title = title_pre + " sentiment by location within story"
    plt.title(title)

    plt.ylim(0.00, 0.17)
    if len(pdata) > 1:
        plt.legend(loc="best", prop=legendFont)

def story_lengths(index, agg, log_bins=True, metric="words"):
    """Plot a histogram depicting the lengths of stories on fimfiction
    """

    plt.figure(figsize=(14, 8), dpi=192)
    if metric == "words":
        lengths = [s["words"] for s in index.values()]
    else:
        lengths = agg["story_lengths"]
    lengths.sort()
    # As of now, there are only 6 stories > 100000 sentences in length:
    # 100545, 106312, 106491, 133191, 136195, 151190 sentences
    # They are not even visible on a histogram
    lengths = [l for l in lengths if l < 100000]
    if log_bins:
        bins = [int(10**(i*5/100)) for i in range(101)]
        bins = list(range(1, 11)) + [i for i in bins if i>10]
    else:
        bins=10000
    plt.hist(lengths, bins=bins)
    plt.xscale("log")

    plt.xlabel("Length ({})".format(metric))
    plt.ylabel("Count")
    plt.title("Number of stories by length")

def character_mentions(agg, chars=characters.keys(), mode="sentence"):
    """Plot the number of times each character is mentioned by name
    """
    pdata = []
    for char in chars:
        pdata.append([agg["char_mentions"][char]["in_a_" + mode], char])

    pdata.sort(reverse=True)
    labels = [p[1] for p in pdata]
    xdata = range(len(pdata))
    ydata = [p[0] for p in pdata]
    colors_ = [colors.get(p[1], "#000000") for p in pdata]
    for lbl, x, y, c in zip(labels, xdata, ydata, colors_):
        plt.bar(x, y, color=c, label=lbl)
    # pdata is now sorted by number of mentions

    plt.ylabel("Count")
    mode_plural = "sentences" if mode == "sentence" else "stories"
    plt.title("Number of {} in which a character appears by name".format(mode_plural))
    # No x ticks.
    plt.xticks([], [])

    plt.legend(loc="best", prop=legendFont)

def char_pairs(agg):
    """Plot the most common character pairings (based on the number of
    stories that mention the character at least once).
    """
    # Only consider pairs of 2+ characters
    eligible = [k for k in agg["char_pairs"].keys() if "," in k]
    top = sorted(eligible, key=lambda p: agg["char_pairs"][p]["in_a_story"], reverse=True)[:12]
    for idx, pairname in enumerate(top):
        plt.bar(idx, agg["char_pairs"][pairname]["in_a_story"], label="#{}. {}".format(idx+1, pairname))

    plt.ylabel("Count")
    plt.title("Most common characters to appear in the same story")
    plt.xticks([i+0.5 for i in range(len(top))], [str(1+i) for i in range(len(top))])

    plt.legend(loc="best", prop=legendFont)
    
def most_common_words(agg, char="text"):
    """Plot the words most commonly associated with the given character
    """
    # Create counts of all words that are found alongside ANY character
    all_words = {}
    for c in characters:
        for w, v in agg["associations"][c].items():
            all_words[w] = all_words.get(w, 0) + v
    # Normalize:
    num_words = sum(all_words.values())
    for k, v in all_words.items():
        all_words[k] = v/num_words

    def is_nontrivial_word(w, norm):
        """Avoid reporting uninteresting words.
        """
        return norm > 1.5*all_words.get(w, 0)

    assoc = agg["associations"][char]
    num_words = sum(assoc.values())
    # Filter non-interesting words and ones which are part of the character's name
    ranked = sorted(assoc.keys(), key=lambda w: assoc[w], reverse=True)
    eligible = (w for w in ranked if is_nontrivial_word(w, norm=assoc[w]/num_words) and w not in char.lower().split(" "))
    top = [next(eligible) for i in range(20)]

    for idx, word in enumerate(top):
        plt.bar(idx, assoc[word], label="#{}. {}".format(1+idx, word))
    plt.ylabel("Count")
    if char == "text":
        title = "Most common words found across all text on fimfiction"
    else:
        title = "Most common words found in sentences where {} is mentioned by name".format(char)
    plt.title(title)

    plt.xticks([i+0.5 for i in range(len(top))], [str(1+i) for i in range(len(top))])

    plt.legend(loc="best", prop=legendFont, ncol=2)

def most_common_nonwords(agg, char="text"):
    """Plot the most common non-words
    """
    dictionary = enchant.Dict("en_US")
    def is_nonword(w):
        if w == "": return False
        is_nw = w not in fim_words and not dictionary.check(w) \
          and not any(similar.lower().replace("-","")==w for similar in dictionary.suggest(w))
        if w.endswith("'s"):
            is_nw = is_nw and is_nonword(w[:-2])
        if "-" in w:
            is_nw = is_nw and any(is_nonword(k) for k in w.split("-"))
        return is_nw

    assoc = agg["associations"][char]
    ranked = sorted(assoc.keys(), key=lambda w: assoc[w], reverse=True)
    eligible = (w for w in ranked if is_nonword(w))
    top = [next(eligible) for i in range(20)]

    for idx, word in enumerate(top):
        plt.bar(idx, assoc[word], label="#{}. {}".format(1+idx, word))

    plt.ylabel("Count")
    if char == "text":
        title = "Most common non-words found across all text on fimfiction"
    else:
        title = "Most common non-words found in sentences where {} is mentioned by name".format(char)
    plt.title(title)

    plt.xticks([i+0.5 for i in range(len(top))], [str(1+i) for i in range(len(top))])

    plt.legend(loc="best", prop=legendFont, ncol=2)

def rating_vs_length(index, metric="words", method="scatter"):
    """Plot a histogram of avg like:(like+dislike) ratio vs length of story.
    metric can be "words" or "titlelen" or "date".
    method can be "linear" or "scatter" to indicate the display formate.
    """
    # (length, like:dislike)
    dpoints = []
    for story in index.values():
        valid, rating = story_rating(story, 1)
        if valid:
            if metric == "words":
                x = story["words"]
            if metric == "titlelen":
                # Titles can somehow be None.
                x = len(story["title"] or "")
            if metric == "date":
                chapters = story["chapters"]
                x = sum(c["date_modified"] for c in chapters)/len(chapters)
            dpoints.append((x, rating))

    dpoints.sort(reverse=True)

    if method=="scatter":
        # Only select a few points to avoid over-crowding.
        x, y = [i[0] for i in dpoints], [i[1] for i in dpoints]
        plt.scatter(x, y, alpha=0.1)
        plt.ylim(-1, 1)
        #plt.hexbin(x, y, xscale=xscale, gridsize=32)
    else:
        # Slice the datapoints to sample the average ratio at discrete ranges
        plot_points = []
        slice_size = 10000
        slice_distance = 500
        for i in range(0, len(dpoints)-slice_size+1, slice_distance):
            rng = dpoints[i:i+slice_size]
            avg_length = sum(i[0] for i in rng)/len(rng)
            if metric == "date":
                avg_length = datetime.datetime.fromtimestamp(avg_length)
            avg_rating = sum(i[1] for i in rng)/len(rng)
            plot_points.append((avg_length, avg_rating))
        plot_func = plt.plot_date if metric == "date" else plt.plot
        plot_func([i[0] for i in plot_points], [i[1] for i in plot_points], '-', lw=2.5)

    # Labels
    plt.ylabel("(likes-dislikes) / (likes+dislikes)")
    if metric == "words":
        plt.xlabel("Story length (words)")
        plt.xlim([1e2, 1e6])
        plt.xscale("log")
        plt.title("Average rating vs story length")
    elif metric == "titlelen":
        plt.xlabel("Title length (chars)")
        plt.title("Average rating vs title length")
    elif metric == "date":
        plt.xlabel("date")
        plt.title("Average rating vs date published")



def most_common_titles(index):
    """Histogram of the most-used titles
    """

    titles = {}
    for story in index.values():
        t = story["title"]
        titles[t] = titles.get(t, 0) + 1

    top = list(titles.items())
    top.sort(key=lambda t: t[1], reverse=True)
    top = top[:10]

    for idx, (title, count) in enumerate(top):
        plt.bar(idx, count, label="#{}. {}".format(1+idx, title))

    plt.ylabel("Count")
    plt.title("The most common story titles on Fimfiction")

    plt.xticks([i+0.5 for i in range(len(top))], [str(1+i) for i in range(len(top))])

    plt.legend(loc="best", prop=legendFont, ncol=2)

def story_status_distr(index):
    """Pie chart of story_status distribution (Incomplete, Hiatus, ...)
    """
    plt.figure(figsize=(10, 8), dpi=192)

    statuses = {}
    for story in index.values():
        s = story["status"]
        statuses[s] = statuses.get(s, 0) + 1

    statuses = sorted(statuses.items())
    explode = [2000/(25000+s[1]) for s in statuses]
    plt.pie([s[1] for s in statuses], labels=[s[0] for s in statuses], explode=explode, autopct='%1.0f%%')

    plt.title("Story status distribution", y=1.08)
    # Make the pie chart circular
    plt.axis("equal")

def rating_vs_char(index, agg, chars=main6):
    """Average the rating of all stories for which a given character appears.
    So so for each character & plot adjacently.
    """
    char_ratings = {}
    for c in chars:
        counts = agg["char_mentions"][c]["in_stories"]
        # extract the stories in which the character appears
        in_stories = [k for (k, count) in counts.items() if count]
        ratings = []
        for story_id in in_stories:
            valid, rating = story_rating(index[story_id])
            if valid:
                ratings.append(rating)
        print("found {} valid ratings for {}, avg: {}".format(len(ratings), c, mean(ratings)))
        char_ratings[c] = mean(ratings)

    # Sort by descending rating
    chardata = sorted(char_ratings.items(), key=lambda i: -i[1])

    labels = [c[0] for c in chardata]
    xdata = range(len(chardata))
    ydata = [c[1] for c in chardata]
    colors_ = [colors.get(c[0], "#000000") for c in chardata]
    for lbl, x, y, c in zip(labels, xdata, ydata, colors_):
        plt.bar(x, y, color=c, label=lbl)

    plt.ylabel("(likes-dislikes)/(likes+dislikes)")
    plt.title("Average story rating based on character appearances")
    plt.ylim(floorto(chardata[-1][1], 0.05), ceilto(chardata[0][1], 0.05))
    # No xticks
    plt.xticks([], [])

    plt.legend(loc="best", prop=legendFont)



figure_functions = { \
    "char_senti_by_month.png": char_senti_by_month,
    "char_senti_by_month_smooth.png": lambda agg: char_senti_by_month(agg, do_smooth=True),
    "char_senti_by_month_all_smooth.png": lambda agg: char_senti_by_month(agg, do_smooth=True, chars=characters, ylim=(-.15,.5)),
    "text_senti_by_month.png": lambda agg: char_senti_by_month(agg, chars=("text",)),
    "text_senti_by_month_smooth.png": lambda agg: char_senti_by_month(agg, chars=("text",), do_smooth=True),
    "text_senti_by_storyarc.png": text_senti_by_storyarc,
    "char_senti_by_storyarc.png": lambda agg: text_senti_by_storyarc(agg, chars=main6),
    "text_senti_by_storyarc_binned.png": lambda agg: text_senti_by_storyarc(agg, arcs=("_short", "_med", "_long")),
    "char_senti_by_storyarc_binned.png": lambda agg: text_senti_by_storyarc(agg, chars=main6, arcs=("_short", "_med", "_long")),
    "char_senti_by_storyarc_short.png": lambda agg: text_senti_by_storyarc(agg, chars=main6, arcs=("_short",)),
    "char_senti_by_storyarc_med.png": lambda agg: text_senti_by_storyarc(agg, chars=main6, arcs=("_med",)),
    "char_senti_by_storyarc_long.png": lambda agg: text_senti_by_storyarc(agg, chars=main6, arcs=("_long",)),
    "story_lengths.png": story_lengths,
    "story_lengths_sentences.png": lambda index, agg: story_lengths(index, agg, metric="sentences"),
    "story_lengths_lin_bins.png": lambda index, agg: story_lengths(index, agg, log_bins=False),
    "character_mentions_in_a_sentence.png": character_mentions,
    "character_mentions_in_a_story.png": lambda agg: character_mentions(agg, mode="story"),
    "char_pairs.png": char_pairs,
    "most_common_words.png": most_common_words,
    "most_common_words_aj.png": lambda agg: most_common_words(agg, "Applejack"),
    "most_common_words_fs.png": lambda agg: most_common_words(agg, "Fluttershy"),
    "most_common_words_pp.png": lambda agg: most_common_words(agg, "Pinkie Pie"),
    "most_common_words_rd.png": lambda agg: most_common_words(agg, "Rainbow Dash"),
    "most_common_words_ra.png": lambda agg: most_common_words(agg, "Rarity"),
    "most_common_words_ts.png": lambda agg: most_common_words(agg, "Twilight Sparkle"),
    "most_common_nonwords.png": most_common_nonwords,
    "most_common_nonwords_aj.png": lambda agg: most_common_nonwords(agg, "Applejack"),
    "most_common_nonwords_fs.png": lambda agg: most_common_nonwords(agg, "Fluttershy"),
    "most_common_nonwords_pp.png": lambda agg: most_common_nonwords(agg, "Pinkie Pie"),
    "most_common_nonwords_rd.png": lambda agg: most_common_nonwords(agg, "Rainbow Dash"),
    "most_common_nonwords_ra.png": lambda agg: most_common_nonwords(agg, "Rarity"),
    "most_common_nonwords_ts.png": lambda agg: most_common_nonwords(agg, "Twilight Sparkle"),
    "rating_vs_length.png": rating_vs_length,
    "rating_vs_length_linear.png": lambda index: rating_vs_length(index, method="linear"),
    "rating_vs_title_length.png": lambda index: rating_vs_length(index, "titlelen"),
    "rating_vs_title_length_linear.png": lambda index: rating_vs_length(index, "titlelen", method="linear"),
    "rating_vs_date.png": lambda index: rating_vs_length(index, "date"),
    "rating_vs_date_linear.png": lambda index: rating_vs_length(index, "date", method="linear"),
    "most_common_titles.png": most_common_titles,
    "story_status_distr.png": story_status_distr,
    "rating_vs_char.png": rating_vs_char,
    "rating_vs_char_all.png": lambda index, agg: rating_vs_char(index, agg, chars=characters.keys()),
}


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: {} <index.json> <aggregated.json> <output image file>".format(sys.argv[0]))
    else:
        index_path, aggregated_path, out_path = sys.argv[1:]
        gen_figure = figure_functions[os.path.split(out_path)[-1]]

        # Lazy-load aggregated.json and index.json
        argspec = inspect.getargspec(gen_figure)
        need_agg, need_index = "agg" in argspec[0], "index" in argspec[0]

        kwargs = {}
        if need_agg:
            kwargs["agg"] = json.loads(open(aggregated_path, "r").read())
        if need_index:
            kwargs["index"] = json.loads(open(index_path, "r").read())

        plt.figure(figsize=(12, 8), dpi=192)
        out_figure = gen_figure(**kwargs)
        plt.savefig(out_path)
