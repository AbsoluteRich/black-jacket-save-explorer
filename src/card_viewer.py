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
        s: data.Save,
        db: data.Database,
        w: Site,
        lbl_card: Label,
        grd_card: Grid,
    ) -> None:
        self.save = s
        self.db = db

        self.images = wiki.ImageFetcher(w)

        self.lbl_card = lbl_card
        self.grd_card = grd_card

    def display_card_selector(self, callback: Callable[[Select, Dialog], None]) -> None:
        with ui.dialog() as dlg_all_cards, ui.card():
            options = {}

            for group, suit_or_set, guid in self.db.iterate_cards():
                value = self.db["cards"][group][suit_or_set][guid]
                options[guid] = game.get_readable_name(group, suit_or_set, value)

            sel_all_cards = ui.select(options, with_input=True)
            ui.button(
                "Save", on_click=lambda s=sel_all_cards, d=dlg_all_cards: callback(s, d)
            )
            ui.button("Cancel", on_click=dlg_all_cards.close)
        dlg_all_cards.open()

    # Button callbacks
    def set_vfx(self, card_index: int) -> None:
        with ui.dialog() as dlg_vfx, ui.card():
            for vfx in self.save["DeckSave"]["GameCardSaves"][card_index]["VfxOptions"]:
                # Save needs to be explicitly called here, because of weird Python magic, bind_value bypasses
                # __setitem__
                ui.checkbox(vfx).bind_value(
                    self.save["DeckSave"]["GameCardSaves"][card_index]["VfxOptions"],
                    vfx,
                ).on_value_change(lambda: self.save.save())
            ui.button("Close", on_click=dlg_vfx.close)
        dlg_vfx.open()

    def add_card(self) -> None:
        def close_and_save(s: Select, d: Dialog) -> None:
            if s.value is None:
                return
            self.save.add_card(guid=s.value)
            d.close()
            self.render.refresh()

        self.display_card_selector(close_and_save)

    def duplicate_card(self, card_index: int) -> None:
        self.save.add_card(
            guid=None, card_data=self.save["DeckSave"]["GameCardSaves"][card_index]
        )
        self.render.refresh()

    def modify_card(self, card_index: int) -> None:
        def close_and_save(s: Select, d: Dialog) -> None:
            self.save["DeckSave"]["GameCardSaves"][card_index]["GameCardGuid"] = s.value
            self.save.save()
            d.close()
            self.render.refresh()

        self.display_card_selector(close_and_save)

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
                self.render.refresh()
                return

    def remove_card(self, card_index: int) -> None:
        del self.save["DeckSave"]["GameCardSaves"][card_index]
        self.save.save()
        self.render.refresh()

    # UI handling
    @ui.refreshable_method
    def render(self) -> None:
        cards = self.save["DeckSave"]["GameCardSaves"]
        self.lbl_card.set_text(f"Cards ({len(cards)})")

        with self.grd_card:
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
                ) as img_card, ui.context_menu():
                    img_card.set_source(url)

                    ui.menu_item(
                        "Duplicate",
                        on_click=lambda c=card_index: self.duplicate_card(c),
                    )

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
