from collections.abc import Callable

import mwcleric as mw
from nicegui import ui
from nicegui.elements.dialog import Dialog
from nicegui.elements.grid import Grid
from nicegui.elements.label import Label
from nicegui.elements.select import Select

import data
import game
import wiki_images


class CardViewer:
    # Private functions
    def __init__(
        self,
        s: data.Save,
        db: data.Database,
        w: mw.wikigg_client.Site,
        lbl_card: Label,
        grd_card: Grid,
    ) -> None:
        self.save = s
        self.db = db

        self.images = wiki_images.ImageFetcher(w)

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
                ).on_value_change(self.save.save)
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


@ui.page("/content")
def page() -> None:
    save = data.Save()
    database = data.Database()
    wiki = mw.wikigg_client.Site("blackjacket.wiki.gg", path="/")

    # Initialise all UI elements
    ui.menu()
    lbl_cards = ui.label("Cards").classes("text-lg font-bold")

    # Card viewer
    with ui.card().classes("w-full"):
        btn_add = ui.button("Add")
        grd_cards = ui.grid(columns=6)

    # Artefacts
    ui.label("Artefacts").classes("text-lg font-bold")
    with ui.card().classes("w-full"):
        ui.label("Placeholder!")

    # Footer
    with ui.footer().classes("bg-slate-900"):
        with ui.row().classes("size-full"):
            # Seed - changing it is unlikely to have useful results, so this is read-only
            with ui.row().classes("items-center gap-2 no-wrap"):
                ui.label("Seed: ").classes("font-bold")
                lbl_seed = ui.label()

            # Stash coins
            with ui.row().classes("items-center gap-2 no-wrap"):
                ui.label("Stash Coins: ").classes("font-bold")
                num_stash = (
                    ui.number(min=0, value=0).props("dense dark").classes("w-20")
                )

            # Winner pot coins
            with ui.row().classes("items-center gap-2 no-wrap"):
                ui.label("Winner's Pot Coins: ").classes("font-bold")
                num_pot = ui.number(min=0, value=0).props("dense dark").classes("w-20")

            btn_edit = ui.button("Edit Other Values").props("dense")

    # Bind functionality to UI
    cv = CardViewer(save, database, wiki, lbl_cards, grd_cards)
    btn_add.on_click(cv.add_card)
    # Todo: This can be implemented with ui.json_editor
    btn_edit.on_click(lambda: ui.notify("This feature is a work in progress!"))
    cv.render()

    lbl_seed.set_text(save["Seed"])

    num_stash.validation = num_pot.validation = {
        "Coins are over the cap. ALL of the excess coins will break if you gain new coins.": lambda x: x
        <= 15
    }

    # WARNING: Abstraction breaking occurs here
    num_stash.bind_value(save.data, "PlayerCoins").on_value_change(save.save)
    num_pot.bind_value(save.data, "WinnersPotCoins").on_value_change(save.save)
