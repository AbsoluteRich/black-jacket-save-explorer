import data


def prompt_entry():
    group = input("Card type (blank/awakened/face): ").lower()

    if group == "face":
        suit_or_set = input("Set: ")
    else:
        suit_or_set = input("Suit: ")

    # We're not doing comparisons, so casefold is unnecessarily aggressive
    suit_or_set = suit_or_set.lower()
    value = input("Value: ").title()

    return group, suit_or_set, value


if __name__ == "__main__":
    save = data.Save()
    database = data.Database()

    print("*** Data Collection ***")
    for current in range(len(save["DeckSave"]["GameCardSaves"])):  # type: ignore
        guid = save["DeckSave"]["GameCardSaves"][current]["GameCardGuid"]

        if database.find(guid) is None:  # type: ignore
            print(f"{guid} does not exist. Marking it as bloody.")

            save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Bloody"] = True
            save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Sliced"] = True
            hollow = save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Ghostly"]
            if hollow:
                save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Ghostly"] = False  # fmt: skip

            try:
                print("What card is this?")
                group, suit_or_set, value = prompt_entry()
                data.insert_or_create(database, group, suit_or_set, value)

            finally:
                # fmt: off
                save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Bloody"] = False
                save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Sliced"] = False
                if hollow:
                    save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Ghostly"] = True
                # fmt: on

    print("*** Deck Analysis ***")
    for current in range(len(save["DeckSave"]["GameCardSaves"])):
        guid = save["DeckSave"]["GameCardSaves"][current]["GameCardGuid"]
        group, suit_or_set, value = database.find(guid)  # type: ignore

        match group:
            case "awakened":
                try:
                    value = int(value)
                    print(f"Awakened {value} of {suit_or_set.title()}")
                except ValueError:
                    if value == "Ace":
                        print(f"Awakened {value} of {suit_or_set.title()}")
                    else:
                        print(value)

            case "blank":
                if suit_or_set == "death":
                    print(f"{value} of {suit_or_set.title()}")
                else:
                    print(f"Blank {value} of {suit_or_set.title()}")
            case "face":
                print(value)
