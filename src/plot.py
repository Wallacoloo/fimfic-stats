#!/usr/bin/python
"""Plots the various aggregated data
"""

# Note: this code depends on Plotly, but DOES NOT REQUIRE AN ONLINE LICENSE.
# NO setup is required for plotly, except installation of python-plotly
# (through pip or your OS package manager)
import json, os.path, sys
import plotly.plotly as py
from plotly.graph_objs import Scatter, Figure, Layout

from common import main6

def char_senti_by_month(agg):
    """Create a plot displaying typical character sentiment
    on fimfiction vs time.
    """
    data = [Scatter(x=[1, 2, 3], y=[3, 1, 6])]
    layout = Layout(title="Character Sentiment vs. Time")
    fig = Figure(data=data, layout=layout)
    return fig


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
        py.image.save_as(out_figure, out_path)
