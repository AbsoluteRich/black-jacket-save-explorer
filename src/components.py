from nicegui import ui

import data


def placeholder(text: str, width: int = 315, height: int = 520) -> str:
    return f"https://placehold.co/{width}x{height}?text={text.replace(' ', '+')}"


def render_editor(save: data.Save, database: data.Database) -> None:
    cards = range(len(save["DeckSave"]["GameCardSaves"]))
    
    ui.label(f"Cards ({len(cards)})").classes("text-lg font-bold")

    with ui.grid(columns=8):
        for card in cards:
            guid = save["DeckSave"]["GameCardSaves"][card]["GameCardGuid"]  # fmt: skip
            res = database.find(guid)

            if res is None:
                ui.label("Card not found!")
            else:
                group, suit_or_set, value = res

                ui.image(placeholder(f"{group},{suit_or_set},{value}")).classes(
                    "w-[315px] max-w-16"
                ).props("fit=contain")
