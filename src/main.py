import mwcleric as mw
from nicegui import ui

import card_viewer
import data

if __name__ in {"__main__", "__mp_main__"}:
    save = data.Save()
    database = data.Database()
    wiki = mw.wikigg_client.Site("blackjacket.wiki.gg", path="/")

    with ui.tabs().classes("w-full") as tabs:
        editor_tab = ui.tab("Save Editor")
        db_tab = ui.tab("Database Inspector")

    with ui.tab_panels(tabs, value=editor_tab).classes("w-full"):
        with ui.tab_panel(editor_tab):
            # Initialise all UI elements
            heading = ui.label("Cards").classes("text-lg font-bold")
            add_button = ui.button("Add")

            with ui.card().classes("w-full"):
                grid = ui.grid(columns=6)

            edit_button = ui.button("Edit Other Values")

            # Bind functionality to UI
            cv = card_viewer.CardViewer(save, database, wiki, heading, grid)
            add_button.on_click(cv.add_card)
            edit_button.on_click(
                lambda: ui.notify("This feature is a work in progress!")
            )
            cv.render()

        with ui.tab_panel(db_tab):
            # Todo: Implement this with:
            #   * A panel that confirms correcting mappings
            #   * A way to remap database entries
            ui.label("Placeholder!")

    ui.run(dark=None, native=True, reload=False)
