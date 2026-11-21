import mwcleric
from nicegui import ui
from nicegui.elements.grid import Grid
from nicegui.elements.label import Label

import data


# Helper functions
def can_be_awakened(group: str, suit_or_set: str, value: str) -> bool:
    if suit_or_set == "Death" or suit_or_set == "Time" or group == "Face":
        return False

    try:
        int(value)
        return True
    except ValueError:
        if value == "Ace":
            return True
        else:
            return False


# Callbacks
def set_vfx(card_index: int, save: data.Save) -> None:
    with ui.dialog() as dialog, ui.card():
        for vfx in save["DeckSave"]["GameCardSaves"][card_index]["VfxOptions"]:
            # Save needs to be explicitly called here, because of weird Python magic, bind_value bypasses __setitem__
            ui.checkbox(vfx).bind_value(
                save["DeckSave"]["GameCardSaves"][card_index]["VfxOptions"], vfx
            ).on_value_change(lambda: save.save())
        ui.button("Close", on_click=dialog.close)
    dialog.open()


def modify_card(cards: data.Database) -> None:
    with ui.dialog() as dialog, ui.card():
        ui.select(cards.data)
        ui.button("Close", on_click=dialog.close)
    dialog.open()


def remove_card(
    card_index: int,
    save: data.Save,
    database: data.Database,
    wiki: mwcleric.wikigg_client.Site,
    heading: Label,
    grid: Grid,
) -> None:
    del save["DeckSave"]["GameCardSaves"][card_index]
    save.save()
    render_cards(save, database, wiki, heading, grid)


# Rendering
def render_cards(
    save: data.Save,
    database: data.Database,
    wiki: mwcleric.wikigg_client.Site,
    heading: Label,
    grid: Grid,
) -> None:
    cards = save["DeckSave"]["GameCardSaves"]

    heading.set_text(f"Cards ({len(cards)})")
    grid.clear()

    with grid:
        for card_index in range(len(cards)):
            # Read the save file for the current GUID
            guid = save["DeckSave"]["GameCardSaves"][card_index]["GameCardGuid"]
            res = database.find(guid)

            if res is None:
                ui.label(f"Unknown GUID: {guid}")
                continue

            # Process GUID name mapping
            group, suit_or_set, value = res

            group = group.title()
            suit_or_set = suit_or_set.title()

            if value.endswith(" (Difficulty)"):
                value = value[: -len(" (Difficulty)")]

            # Get image from the Black Jacket wiki (WARNING: API requests begin here)
            if group.casefold() == "face":
                image = wiki.images[f"Card {suit_or_set} {value}.png"]
            else:
                image = wiki.images[f"Card {suit_or_set} {value} {group}.png"]

            if image.imageinfo == {}:
                ui.label(f"Image not found: {group} {suit_or_set} {value}")
                continue

            # Create a new image
            with ui.image().classes("w-24").props(
                "fit=contain"
            ) as gui_image, ui.context_menu():
                gui_image.source = image.imageinfo["url"]

                ui.menu_item("Set VFX", on_click=lambda c=card_index: set_vfx(c, save))

                if can_be_awakened(group, suit_or_set, value):
                    if group == "Blank":
                        ui.menu_item("Awaken")
                    elif group == "Awakened":
                        ui.menu_item("Dampen")
                    else:
                        ui.menu_item("Awaken").set_enabled(False)

                ui.menu_item(
                    "Replace", on_click=lambda c=card_index: modify_card(database)
                )
                ui.menu_item(
                    "Remove",
                    on_click=lambda c=card_index: remove_card(
                        c, save, database, wiki, heading, grid
                    ),
                )
