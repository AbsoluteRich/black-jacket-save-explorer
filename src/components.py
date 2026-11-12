import mwcleric
from nicegui import ui

import data


def placeholder(text: str, width: int = 315, height: int = 520) -> str:
    return f"https://placehold.co/{width}x{height}?text={text.replace(' ', '+')}"


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
                value = value[:-len(" (Difficulty)")]

            if group.casefold() == "face":
                # Todo: Fix when the wiki side is fixed
                image = wiki.images[f"Card {suit_or_set} {value}.png"]
            else:
                image = wiki.images[f"Card {suit_or_set} {value} {group}.png"]

            if image.imageinfo == {}:
                ui.label(f"Image not found: {group} {suit_or_set} {value}")
                continue

            ui.image(image.imageinfo["url"]).classes("w-24").props("fit=contain")
