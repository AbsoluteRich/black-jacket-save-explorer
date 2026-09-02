import data


def prompt_entry():
    group = input("Card type (blank/awakened/face): ").lower()

    if group == "face":
        set_or_suit = input("Set: ")
    else:
        set_or_suit = input("Suit: ")

    # We're not doing comparisons, so casefold is unnecessarily aggressive
    set_or_suit = set_or_suit.lower()

    if group == "face":
        name_or_value = input("Name: ").title()
    else:
        name_or_value = input("Value: ").title()

    return group, set_or_suit, name_or_value


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
            save.save()

            try:
                print("What card is this?")
                group, suit_or_set, value = prompt_entry()
                data.insert_or_create(database, value, group, suit_or_set, guid)

            finally:
                # fmt: off
                save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Bloody"] = False
                save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Sliced"] = False
                if hollow:
                    save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Ghostly"] = True
                save.save()
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

    input("\nPress Enter to exit.")
