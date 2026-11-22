import abc
import json
from collections.abc import Generator
from typing import Any

import tomlkit as toml

import config


class File(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        self.data = {}

    def __getitem__(self, key: Any) -> Any:
        return self.data[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self.data[key] = value
        self.save()

    @abc.abstractmethod
    def save(self) -> None:
        pass


class Save(File):
    def __init__(self) -> None:
        with open(config.GAME_SAVE) as f:
            self.data = json.load(f)

    def save(self) -> None:
        with open(config.GAME_SAVE, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_card(self, guid: str | None, card_data: dict | None = None):
        if card_data is None:
            if guid is None:
                raise ValueError("`guid` must be provided if `card_data` is None!")

            self.data["DeckSave"]["GameCardSaves"].append(
                {
                    "GameCardGuid": guid,
                    "VfxOptions": {
                        "Sliced": False,
                        "Bloody": False,
                        "Ghostly": False,
                        "Marked": False,
                        "WineDrip": False,
                        "Devour": False,
                        "Shame": False,
                    },
                    "CardModifiers": [],
                    "GameCardModuleData": [],
                }
            )
        else:
            self.data["DeckSave"]["GameCardSaves"].append(card_data)

        # Since this uses the underlying dictionary rather than calling __setitem__, we have to save manually here
        self.save()


class Database(File):
    def __init__(self) -> None:
        with open(config.DATABASE_FILE) as f:
            self.data: toml.TOMLDocument = toml.load(f)

    def iterate_cards(self) -> Generator[tuple[str, str, str]]:
        for group in self.data["cards"]:
            for suit_or_set in self.data["cards"][group]:
                for guid in self.data["cards"][group][suit_or_set]:
                    yield group, suit_or_set, guid

    def find_card(self, to_find: str) -> tuple[str, str, str] | None:
        for group, suit_or_set, guid in self.iterate_cards():
            if guid == to_find:
                value = self.data["cards"][group][suit_or_set][guid]
                return group, suit_or_set, value

        return None

    def save(self) -> None:
        with open(config.DATABASE_FILE, "w") as f:
            toml.dump(self.data, f)
