About
------
fimfiction.net is the main place where bronies publish fanfiction. It's home to over 130,000 stories (and growing daily) and 9 GB of unformatted text. With this much data on our hooves, we can finally figure out who the best pony is (among other things).

Sentiment analysis is the act of looking at some text and quantitatively
measuring its sentiment.
For example, we might assign a score of -0.6 to the text
`Cows are terrifying because they're fat and they talk a lot`
because it's spoken in a "negative" manner. On the other hand,
`Your smile fills me with glee`
might get a score of +0.8.

By analyzing the sentiment of each sentence in which a given character
appears across the entire set of stories available to us, we can glean
some information about which characters are spoken of in the most positive
light. We can also track this data across time to see how the general mood
of writings on fimfiction has changed over time, or even the ways in which
it tends to change throughout individual stories (beginning, middle, end).

Besides sentiment analysis, we can also track which words occur nearby
each character's name inside the text and use this to see which words
(or non-words) are most associated with each character. We can also see
which characters are most often paired with each other.

Finally, we can perform analysis on the story metadata to see how story
ratings correlate to things like the length of the story or the time at
which it was published.



Pre-requisites
------

Performing the analysis requires `ebook-convert`, as well as a python 3
installation, the python3 `nltk` library and the SentiWordNet database
installed systemwide or into `~/nltk_data`.
The `pyenchant` Python library is also needed (specifically, the `en_US` dictionary).

For Arch users, the relevant packages can be installed via:
```
# pacman -S ebook-convert python-nltk nltk-data python-pyenchant
```

You will also need to download the fimfiction dump and extract it to `res/fimfarchive-20160525` (the path may be edited at the top of the Makefile
for future dumps).
The fimfiction dumps can be found on JockeTF's
[website](http://jocketf.se/files/fimfarchive/), in
[this](https://www.reddit.com/r/mylittlepony/comments/4l5o3p/fimfarchive_20160525_released_all_stories_on/)
reddit thread or they can be obtained by running the fimfarchive code
[here](https://github.com/JockeTF/fimfarchive).



Building
------
Just navigate to the repository directory and type
```
make
```

This will first convert the .epub books to plaintext, perform
sentiment and word analysis on each story in isolation, aggregate the
results, and finally generate plots in the `build/plots/` directory.

If you have multiple cores, I highly advise making use of those with
`make -j<num_cores>`. The entire process takes 2-3 days on a modern mobile i5 processor and expect the `build/` directory to grow to around 20 GB.
You can interrupt the build process at any time, and `make` will pick up where it left off the next time you invoke it.



Results
------

Results can be found [here](http://mooooo.ooo/fimfic-best-pony/) along with a brief write-up.



License
------

All code in this repository is licensed under the terms of the GPL.
