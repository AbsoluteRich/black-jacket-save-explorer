import mwcleric
from nicegui import ui

import data


def set_vfx(card_index: int, save: data.Save) -> None:
    with ui.dialog() as dialog, ui.card():
        for vfx in save["DeckSave"]["GameCardSaves"][card_index]["VfxOptions"]:
            # Save needs to be explicitly called here, because of weird Python magic, bind_value bypasses __setitem__
            ui.checkbox(vfx).bind_value(
                save["DeckSave"]["GameCardSaves"][card_index]["VfxOptions"], vfx
            ).on_value_change(lambda: save.save())
        ui.button("Close", on_click=dialog.close)
    dialog.open()


def modify_card(guid: str, remove=False) -> None:
    print(f"Preparing {guid} for {"removal" if remove else "replacement"}")


def render_cards(
    save: data.Save, database: data.Database, wiki: mwcleric.wikigg_client.Site
) -> None:
    cards = save["DeckSave"]["GameCardSaves"]
    ui.label(f"Cards ({len(cards)})").classes("text-lg font-bold")

    with ui.grid(columns=8):
        for card in range(len(cards)):
            guid = save["DeckSave"]["GameCardSaves"][card]["GameCardGuid"]  # fmt: skip
            res = database.find(guid)

            if res is None:
                ui.label(f"Unknown GUID: {guid}")
                continue

            group, suit_or_set, value = res

            group = group.title()
            suit_or_set = suit_or_set.title()

            if value.endswith(" (Difficulty)"):
                value = value[: -len(" (Difficulty)")]

            if group.casefold() == "face":
                # Todo: Fix when the wiki side is fixed
                image = wiki.images[f"Card {suit_or_set} {value}.png"]
            else:
                image = wiki.images[f"Card {suit_or_set} {value} {group}.png"]

            print(image.base_title)

            if image.imageinfo == {}:
                ui.label(f"Image not found: {group} {suit_or_set} {value}")
                continue

            with ui.image().classes("w-24").props("fit=contain") as gui_image:
                gui_image.source = image.imageinfo["url"]

                with ui.context_menu():
                    ui.menu_item("Set VFX", on_click=lambda c=card: set_vfx(c, save))
                    ui.menu_item("Replace", on_click=lambda g=guid: modify_card(g))
                    ui.menu_item(
                        "Remove", on_click=lambda g=guid: modify_card(g, remove=True)
                    )
