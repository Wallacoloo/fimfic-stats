#!/usr/bin/python
"""Plots the various aggregated data
"""

import datetime, json, os.path, sys
from math import cos, pi, tan
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from common import main6

# Based on http://helmet.kafuka.org/ponycolors/
colors = {
    "Applejack": "#FCBA63",
    "Fluttershy": "#F0DA75",
    "Pinkie Pie": "#F6B7D2",
    "Rainbow Dash": "#9EDBF8",
    "Rarity": "#BEC2C3",
    "Twilight Sparkle": "#D19FE4",
    "text": "#101010",
}

legendFont = FontProperties()
legendFont.set_size('small')

cot = lambda x: 1/tan(x)

def smooth(month_data):
    """Smooth month-based data so that the long-term trends are more visible
    """
    # Work based on http://www.claysturner.com/dsp/Butterworth%20Filter%20Formulae.pdf
    # data is sampled by months, want trends > 6 months to be visible
    # Use fc =~ 1/6
    fc = 1/12
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

    x = month_data
    y = []
    for n in range(len(x)):
        y.append(filt(x, y, n))

    return y


def char_senti_by_month(agg, chars=main6, do_smooth=False):
    """Create a plot displaying typical character sentiment
    on fimfiction vs time.
    """
    plt.figure(figsize=(12, 8), dpi=180)

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


figure_functions = { \
    "char_senti_by_month.png": char_senti_by_month,
    "char_senti_by_month_smooth.png": lambda agg: char_senti_by_month(agg, do_smooth=True),
    "text_senti_by_month.png": lambda agg: char_senti_by_month(agg, chars=("text",)),
    "text_senti_by_month_smooth.png": lambda agg: char_senti_by_month(agg, chars=("text",), do_smooth=True),
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
