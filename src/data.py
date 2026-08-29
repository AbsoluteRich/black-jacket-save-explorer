import abc
import json
from typing import Any

import tomlkit as toml
from tomlkit.exceptions import NonExistentKey

import config
import main


class File(abc.ABC):
    def __init__(self, data: dict) -> None:
        self.data = data

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
            super().__init__(json.load(f))

    def save(self) -> None:
        with open(config.GAME_SAVE, "w") as f:
            json.dump(self.data, f, indent=4)


class Database(File):
    def __init__(self) -> None:
        with open(config.DATABASE_FILE) as f:
            super().__init__(toml.load(f))

    def find(self, to_find: str) -> tuple[str, str, str] | None:
        for data_group in self.data:
            for data_suit in self.data[data_group]:
                for key in self.data[data_group][data_suit]:
                    if key == to_find:
                        group = data_group
                        suit_or_set = data_suit
                        value = self.data[data_group][data_suit][key]
                        return (group, suit_or_set, value)

        return None

    def save(self) -> None:
        with open(config.DATABASE_FILE, "w") as f:
            toml.dump(self.data, f)


def insert_or_create(
    database: Database, group: str, suit_or_set: str, value: str
) -> None:
    if suit_or_set not in database[group]:
        database[group][suit_or_set] = toml.table()
    database[group][suit_or_set][guid] = value
    database.save()


if __name__ == "__main__":
    print("*** Database Appender ***")
    database = Database()

    while True:
        guid = input("GUID (leave empty to exit): ")

        if guid == "":
            break

        group, suit_or_set, value = main.prompt_entry()
        insert_or_create(database, group, suit_or_set, value)
