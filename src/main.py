import mwcleric as mw
from nicegui import ui

import card_viewer
import data

if __name__ in {"__main__", "__mp_main__"}:
    save = data.Save()
    database = data.Database()
    wiki = mw.wikigg_client.Site("blackjacket.wiki.gg", path="/")

    # Initialise all UI elements
    heading = ui.label("Cards").classes("text-lg font-bold")
    add_button = ui.button("Add")

    with ui.card().classes("w-full"):
        grid = ui.grid(columns=6)

    edit_button = ui.button("Edit Other Values")

    # Bind functionality to UI
    cv = card_viewer.CardViewer(save, database, wiki, heading, grid)
    add_button.on_click(cv.add_card)
    edit_button.on_click(lambda: ui.notify("This feature is a work in progress!"))
    cv.render()

    ui.run(dark=None, native=True, reload=False)
