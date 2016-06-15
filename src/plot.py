#!/usr/bin/python
"""Plots the various aggregated data
"""

import datetime, json, os.path, sys
import matplotlib.pyplot as plt

from common import main6

colors = {
    "Applejack": "#FCBA63",
    "Fluttershy": "#FDF6AE",
    "Pinkie Pie": "#F6B7D2",
    "Rainbow Dash": "#9EDBF8",
    "Rarity": "#BEC2C3",
    "Twilight Sparkle": "#D19FE4"
}

def char_senti_by_month(agg):
    """Create a plot displaying typical character sentiment
    on fimfiction vs time.
    """
    plt.figure

    # Prepare data
    pdata = {}
    for char in main6:
        xdata = [datetime.datetime(year=2010+int(i/12), month=i%12+1, day=1) for i in range(100)]
        ydata = [month["sum"]/max(1, month["count"]) for month in agg["sentiment"][char]["months"] ]
        pdata[char] = [xdata, ydata]

    # Plot data
    for char, cdata in pdata.items():
        plt.plot_date(cdata[0], cdata[1], '-', label=char, color=colors[char])

    # Labels
    plt.xlabel("Year")
    plt.ylabel("Average compound sentiment")
    plt.title("Character sentiment vs. Time")

    #plt.xlim(0, 6)
    #plt.ylim(-5, 80)
    plt.legend(loc="upper left")



figure_functions = { \
    "char_senti_by_month.png": char_senti_by_month
}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <aggregated.json> <output image file>".format(sys.argv[0]))
    else:
        aggregated_path, out_path = sys.argv[1:]
        aggregated = json.loads(open(aggregated_path, "r").read())
        gen_figure = figure_functions[os.path.split(out_path)[-1]]
        out_figure = gen_figure(aggregated)
        plt.savefig(out_path)
