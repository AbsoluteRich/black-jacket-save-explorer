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


class Database(File):
    def __init__(self) -> None:
        with open(config.DATABASE_FILE) as f:
            self.data: toml.TOMLDocument = toml.load(f)

    def iterate(self) -> Generator[tuple[str, str, str]]:
        for group in self.data:
            for suit_or_set in self.data[group]:
                for guid in self.data[group][suit_or_set]:
                    yield group, suit_or_set, guid

    def find(self, to_find: str) -> tuple[str, str, str] | None:
        for group, suit_or_set, guid in self.iterate():
            if guid == to_find:
                guid = self.data[group][suit_or_set][guid]
                return group, suit_or_set, guid

        return None

    def save(self) -> None:
        with open(config.DATABASE_FILE, "w") as f:
            toml.dump(self.data, f)
