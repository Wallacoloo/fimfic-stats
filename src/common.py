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
        "Rainbow Dash": ("Rainbow Dash", "Rainbow", "Dashie", "Dash",),
        "Rarity": ("Rarity",),
        "Twilight Sparkle": ("Twilight Sparkle", "Twilight", "Sparkle",),
        "Spike": ("Spike",),
        # CMC
        "Apple Bloom": ("Apple Bloom", "Applebloom"),
        "Scootaloo": ("Scootaloo",),
        "Sweetie Belle": ("Sweetie Belle", "Sweetie", "Sweetiebelle"),
        "Babs Seed": ("Babs Seed", "Babs", "Babsseed"),
        # Royalty
        # 'Princess' and 'Principal' have no sentiment in VADER, so we
        # don't have to worry about those titles
        "Celestia": ("Celestia",),
        "Luna": ("Luna",),
        "Cadance": ("Cadance", "Cadence"),
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
}

characters_plus_text = dict(text=(), **characters)

main6 = ["Applejack", "Fluttershy", "Pinkie Pie", "Rainbow Dash", "Rarity", "Twilight Sparkle"]

class story_length:
    # Short stories have <= `short' sentences
    short = 100
    med = 1000


def attribute_sentence_to_char(sentence, chars=characters_plus_text, replace=True):
    """Search for any occurrences of the characters' names
    or nicknames inside the sentence, remove them, and then return the
    names of the characters found and a sentence with their names removed.
    """

    c_in_s = {}
    for c, nicks in characters_plus_text.items():
        for nick in nicks:
            if nick in sentence:
                c_in_s[c] = nick
                break

    # Replace all character names with a neutral word
    # sum() is used to flatten the dict items
    if replace:
        for nick in c_in_s.values():
            sentence = sentence.replace(nick, "it")

    return c_in_s.keys(), sentence
