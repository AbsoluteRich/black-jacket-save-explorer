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


def modify_card(
    card_index: int,
    save: data.Save,
    cards: data.Database,
    wiki: mwcleric.wikigg_client.Site,
    heading: Label,
    grid: Grid,
) -> None:
    def close_and_save(d: Dialog, s: Select):
        save["DeckSave"]["GameCardSaves"][card_index]["CardGuid"] = s.value
        save.save()
        d.close()
        render_viewer(save, cards, wiki, heading, grid)

    with ui.dialog() as dialog, ui.card():
        options = {}

        for group, suit_or_set, guid in cards.iterate():
            value = cards[group][suit_or_set][guid]
            options[guid] = get_readable_name(group, suit_or_set, value)

        selection = ui.select(options)
        ui.button("Save", on_click=lambda s=selection: close_and_save(dialog, s))
        ui.button("Cancel", on_click=dialog.close)
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
    render_viewer(save, database, wiki, heading, grid)


# Rendering
def render_viewer(
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
            file_name = get_wiki_name(group, suit_or_set, value)

            # Get image from the Black Jacket wiki (WARNING: API requests begin here)
            image = wiki.images[file_name]

            if image.imageinfo == {}:
                ui.label(f"Image not found: {file_name}")
                continue

            # Create a new image
            with ui.image().classes("w-24").props(
                "fit=contain"
            ) as gui_image, ui.context_menu():
                gui_image.source = image.imageinfo["url"]

                ui.menu_item("Set VFX", on_click=lambda c=card_index: set_vfx(c, save))

                if can_be_awakened(group, suit_or_set, value):
                    if group.casefold() == "blank":
                        ui.menu_item("Awaken")
                    elif group.casefold() == "awakened":
                        ui.menu_item("Dampen")

                ui.menu_item(
                    "Replace",
                    on_click=lambda c=card_index: modify_card(
                        c, save, database, wiki, heading, grid
                    ),
                )
                ui.menu_item(
                    "Remove",
                    on_click=lambda c=card_index: remove_card(
                        c, save, database, wiki, heading, grid
                    ),
                )
