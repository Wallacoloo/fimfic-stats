"""Contains data that may be used across both the analysis and
aggregation (etc) stages.
"""

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
