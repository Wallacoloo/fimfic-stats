#!/usr/bin/python
"""Plots the various aggregated data
"""

import datetime, json, os.path, sys
from math import cos, pi, tan
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

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

legendFont = FontProperties()
legendFont.set_size('small')

cot = lambda x: 1/tan(x)

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


def char_senti_by_month(agg, chars=main6, do_smooth=False):
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

    #plt.xlim(0, 6)
    plt.ylim(0.00, 0.13)
    if len(pdata) > 1:
        plt.legend(loc="best", prop=legendFont)

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

    plt.ylim(0.00, 0.13)
    if len(pdata) > 1:
        plt.legend(loc="best", prop=legendFont)

def story_lengths(agg):
    """Plot a histogram depicting the lengths of stories on fimfiction
    """

    plt.figure(figsize=(14, 8), dpi=180)
    lengths = agg["story_lengths"]
    lengths.sort()
    #print(len([l for l in lengths if l <= 100]))
    #print(len([l for l in lengths if l <= 200]))
    #print(len([l for l in lengths if l >= 1000]))
    #print(len([l for l in lengths if l >= 1500]))
    #print(len([l for l in lengths if l >= 2000]))
    #print(len([l for l in lengths if l >= 2500]))
    #print(len([l for l in lengths if 100 < l < 1000]))
    #print(len([l for l in lengths if 100 < l < 1500]))
    # As of now, there are only 6 stories > 100000 sentences in length:
    # 100545, 106312, 106491, 133191, 136195, 151190 sentences
    # They are not even visible on a histogram
    lengths = [l for l in lengths if l < 100000]
    plt.hist(lengths, bins=10000)
    plt.xscale("log")

    plt.xlabel("Length (sentences)")
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

    plt.legend(loc="best", prop=legendFont)
    



figure_functions = { \
    "char_senti_by_month.png": char_senti_by_month,
    "char_senti_by_month_smooth.png": lambda agg: char_senti_by_month(agg, do_smooth=True),
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
    "character_mentions_in_a_sentence.png": character_mentions,
    "character_mentions_in_a_story.png": lambda agg: character_mentions(agg, mode="story"),
}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <aggregated.json> <output image file>".format(sys.argv[0]))
    else:
        aggregated_path, out_path = sys.argv[1:]
        aggregated = json.loads(open(aggregated_path, "r").read())
        gen_figure = figure_functions[os.path.split(out_path)[-1]]

        plt.figure(figsize=(12, 8), dpi=180)
        out_figure = gen_figure(aggregated)
        plt.savefig(out_path)
