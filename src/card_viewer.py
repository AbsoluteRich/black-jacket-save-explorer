from collections.abc import Callable

from mwcleric.wikigg_client import Site
from nicegui import ui
from nicegui.elements.dialog import Dialog
from nicegui.elements.grid import Grid
from nicegui.elements.label import Label
from nicegui.elements.select import Select

import data
import game
import wiki


class CardViewer:
    # Private functions
    def __init__(
        self,
        save: data.Save,
        db: data.Database,
        w: Site,
        heading: Label,
        grid: Grid,
    ) -> None:
        self.save = save
        self.db = db

        self.images = wiki.ImageFetcher(w)

        self.heading = heading
        self.grid = grid

    def get_card_selection(self, callback: Callable[[Select, Dialog], None]) -> None:
        with ui.dialog() as dialog, ui.card():
            options = {}

            for group, suit_or_set, guid in self.db.iterate_cards():
                value = self.db["cards"][group][suit_or_set][guid]
                options[guid] = game.get_readable_name(group, suit_or_set, value)

            selection = ui.select(options)
            ui.button("Save", on_click=lambda s=selection, d=dialog: callback(s, d))
            ui.button("Cancel", on_click=dialog.close)
        dialog.open()

    # Button callbacks
    def add_card(self) -> None:
        def close_and_save(s: Select, d: Dialog) -> None:
            if s.value is None:
                return

            self.save["DeckSave"]["GameCardSaves"].append(
                {
                    "GameCardGuid": s.value,
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
            self.save.save()
            d.close()
            self.render()

        self.get_card_selection(close_and_save)

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

    def modify_card(self, card_index: int) -> None:
        def close_and_save(s: Select, d: Dialog) -> None:
            self.save["DeckSave"]["GameCardSaves"][card_index]["GameCardGuid"] = s.value
            self.save.save()
            d.close()
            self.render()

        self.get_card_selection(close_and_save)

    def remove_card(self, card_index: int) -> None:
        del self.save["DeckSave"]["GameCardSaves"][card_index]
        self.save.save()
        self.render()

    def flip_card(self, card_index: int) -> None:
        guid = self.save["DeckSave"]["GameCardSaves"][card_index]["GameCardGuid"]
        res = self.db.find_card(guid)

        # If this actually triggers, something has gone horribly wrong
        if res is None:
            return

        group, suit_or_set, value = res

        change_to = "awakened" if group.casefold() == "blank" else "blank"
        for new_guid, new_value in self.db["cards"][change_to][suit_or_set].items():
            if value == new_value:
                self.save["DeckSave"]["GameCardSaves"][card_index][
                    "GameCardGuid"
                ] = new_guid
                self.save.save()
                self.render()
                return

    # UI handling
    def render(self) -> None:
        cards = self.save["DeckSave"]["GameCardSaves"]

        self.heading.set_text(f"Cards ({len(cards)})")
        self.grid.clear()

        with self.grid:
            for card_index in range(len(cards)):
                # Read the save file for the current GUID
                guid = self.save["DeckSave"]["GameCardSaves"][card_index][
                    "GameCardGuid"
                ]
                res = self.db.find_card(guid)

                if res is None:
                    ui.label(f"Unknown GUID: {guid}")
                    continue

                # Process GUID name mapping
                group, suit_or_set, value = res
                file_name = game.get_wiki_name(group, suit_or_set, value)

                # Get image from the Black Jacket wiki (WARNING: API requests begin here)
                success, url = self.images.get_url(file_name)

                if not success:
                    ui.label(f"Image not found: {file_name}")
                    continue

                # Create a new image
                with ui.image().classes("w-24").props(
                    "fit=contain"
                ) as image, ui.context_menu():
                    image.set_source(url)

                    ui.menu_item(
                        "Set VFX", on_click=lambda c=card_index: self.set_vfx(c)
                    )

                    if game.can_be_awakened(group, suit_or_set, value):
                        if group.casefold() == "blank":
                            ui.menu_item(
                                "Awaken",
                                on_click=lambda c=card_index: self.flip_card(c),
                            )
                        elif group.casefold() == "awakened":
                            ui.menu_item(
                                "Dampen",
                                on_click=lambda c=card_index: self.flip_card(c),
                            )

                    ui.menu_item(
                        "Replace", on_click=lambda c=card_index: self.modify_card(c)
                    )
                    ui.menu_item(
                        "Remove", on_click=lambda c=card_index: self.remove_card(c)
                    )
