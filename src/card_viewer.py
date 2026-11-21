import mwcleric
from nicegui import ui
from nicegui.elements.dialog import Dialog
from nicegui.elements.grid import Grid
from nicegui.elements.label import Label
from nicegui.elements.select import Select

import data


# Helpers
def can_be_awakened(group: str, suit_or_set: str, value: str) -> bool:
    if (
        suit_or_set.casefold() == "death"
        or suit_or_set.casefold() == "time"
        or group.casefold() == "face"
    ):
        return False

    return is_card_value(value)


def is_card_value(unknown: str) -> bool:
    try:
        int(unknown)
        return True
    except ValueError:
        if unknown.casefold() == "ace":
            return True
        else:
            return False


def get_readable_name(group: str, suit_or_set: str, value: str) -> str:
    if group.casefold() == "face":
        res = value
    else:
        res = ""

        if suit_or_set.casefold() != "death":
            res += f"{group.title()} "

        res += value

        if is_card_value(value):
            res += f" of {suit_or_set.title()}"

    return res


def get_wiki_name(group: str, suit_or_set: str, value: str) -> str:
    group = group.title()
    suit_or_set = suit_or_set.title()

    if value.endswith(" (Difficulty)"):
        value = value[: -len(" (Difficulty)")]

    if group.casefold() == "face":
        result = f"Card {suit_or_set} {value}.png"
    else:
        result = f"Card {suit_or_set} {value} {group}.png"

    return result


# The big class
class CardViewer:
    def __init__(
        self,
        save: data.Save,
        db: data.Database,
        wiki: mwcleric.wikigg_client.Site,
        heading: Label,
        grid: Grid,
    ) -> None:
        self.save = save
        self.db = db
        self.wiki = wiki
        self.heading = heading
        self.grid = grid

    def set_vfx(self, card_index: int) -> None:
        with ui.dialog() as dialog, ui.card():
            for vfx in self.save["DeckSave"]["GameCardSaves"][card_index]["VfxOptions"]:
                # Save needs to be explicitly called here, because of weird Python magic, bind_value bypasses
                # __setitem__
                ui.checkbox(vfx).bind_value(
                    self.save["DeckSave"]["GameCardSaves"][card_index]["VfxOptions"],
                    vfx,
                ).on_value_change(lambda: self.save.save())
            ui.button("Close", on_click=dialog.close)
        dialog.open()

    def modify_card(
        self,
        card_index: int,
    ) -> None:
        def close_and_save(d: Dialog, s: Select):
            self.save["DeckSave"]["GameCardSaves"][card_index]["CardGuid"] = s.value
            self.save.save()
            d.close()
            self.render()

        with ui.dialog() as dialog, ui.card():
            options = {}

            for group, suit_or_set, guid in self.db.iterate():
                value = self.db[group][suit_or_set][guid]
                options[guid] = get_readable_name(group, suit_or_set, value)

            selection = ui.select(options)
            ui.button("Save", on_click=lambda s=selection: close_and_save(dialog, s))
            ui.button("Cancel", on_click=dialog.close)
        dialog.open()

    def remove_card(
        self,
        card_index: int,
    ) -> None:
        del self.save["DeckSave"]["GameCardSaves"][card_index]
        self.save.save()
        self.render()

    def render(self):
        cards = self.save["DeckSave"]["GameCardSaves"]

        self.heading.set_text(f"Cards ({len(cards)})")
        self.grid.clear()

        with self.grid:
            for card_index in range(len(cards)):
                # Read the save file for the current GUID
                guid = self.save["DeckSave"]["GameCardSaves"][card_index][
                    "GameCardGuid"
                ]
                res = self.db.find(guid)

                if res is None:
                    ui.label(f"Unknown GUID: {guid}")
                    continue

                # Process GUID name mapping
                group, suit_or_set, value = res
                file_name = get_wiki_name(group, suit_or_set, value)

                # Get image from the Black Jacket wiki (WARNING: API requests begin here)
                image = self.wiki.images[file_name]

                if image.imageinfo == {}:
                    ui.label(f"Image not found: {file_name}")
                    continue

                # Create a new image
                with ui.image().classes("w-24").props(
                    "fit=contain"
                ) as gui_image, ui.context_menu():
                    gui_image.source = image.imageinfo["url"]

                    ui.menu_item(
                        "Set VFX", on_click=lambda c=card_index: self.set_vfx(c)
                    )

                    if can_be_awakened(group, suit_or_set, value):
                        if group.casefold() == "blank":
                            ui.menu_item("Awaken")
                        elif group.casefold() == "awakened":
                            ui.menu_item("Dampen")

                    ui.menu_item(
                        "Replace", on_click=lambda c=card_index: self.modify_card(c)
                    )
                    ui.menu_item(
                        "Remove", on_click=lambda c=card_index: self.remove_card(c)
                    )
