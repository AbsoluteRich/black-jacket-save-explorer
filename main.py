import json
from pathlib import Path

import platformdirs
import tomlkit as toml

game_save = Path(platformdirs.user_data_dir() + "Low") / "Mipumi Games" / "BlackJacket"


def flatten_dict(data: dict) -> list:
    # Designed for use within this script
    result = []

    for group in data:
        for suit in data[group]:
            for key in data[group][suit]:
                result.append(key)
                # result[key] = d[group][suit]

    return result


def find_key(to_find: str, data: dict) -> tuple[str, str, str]:
    group = ""
    suit_or_set = ""
    value = ""

    for data_group in data:
        for data_suit in data[data_group]:
            for key in data[data_group][data_suit]:
                if key == to_find:
                    group = data_group
                    suit_or_set = data_suit
                    value = data[data_group][data_suit][key]
                    return (group, suit_or_set, value)

    return (group, suit_or_set, value)


if __name__ == "__main__":
    with open(game_save / "campaignSave.json") as f:
        save = json.load(f)

    with open("database.toml") as f:
        mapped_guids = toml.load(f)

    known_guids = flatten_dict(mapped_guids)

    print("*** Data Collection ***")
    for current in range(len(save["DeckSave"]["GameCardSaves"])):
        guid = save["DeckSave"]["GameCardSaves"][current]["GameCardGuid"]

        if guid not in known_guids:
            print(f"{guid} does not exist. Marking it as bloody.")

            save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Bloody"] = True
            save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Sliced"] = True
            hollow = save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Ghostly"]
            if hollow:
                save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Ghostly"] = False  # fmt: skip

            with open(game_save / "campaignSave.json", "w") as f:
                json.dump(save, f, indent=4)

            try:
                print("What card is this?")
                group = input("Type (blank/awakened/face): ")
                if group == "face":
                    suit_or_set = input("Set: ")
                else:
                    suit_or_set = input("Suit: ")
                # We're not doing comparisons, so casefold is unnecessarily aggressive
                suit_or_set = suit_or_set.lower()
                value = input("Value: ")

                if suit_or_set not in mapped_guids[group]:
                    mapped_guids[group][suit_or_set] = {}

                mapped_guids[group][suit_or_set][guid] = value
                known_guids = flatten_dict(mapped_guids)

                with open("database.toml", "w") as f:
                    toml.dump(mapped_guids, f)

            finally:
                # fmt: off
                save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Bloody"] = False
                save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Sliced"] = False
                if hollow:
                    save["DeckSave"]["GameCardSaves"][current]["VfxOptions"]["Ghostly"] = True
                # fmt: on

                with open(game_save / "campaignSave.json", "w") as f:
                    json.dump(save, f, indent=4)

    print("*** Deck Analysis ***")
    for current in range(len(save["DeckSave"]["GameCardSaves"])):
        guid = save["DeckSave"]["GameCardSaves"][current]["GameCardGuid"]
        group, suit_or_set, value = find_key(guid, mapped_guids)

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
