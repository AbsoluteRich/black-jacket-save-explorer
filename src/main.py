from nicegui import ui

import components
import data

if __name__ in {"__main__", "__mp_main__"}:
    save = data.Save()
    database = data.Database()

    with ui.tabs().classes("w-full") as tabs:
        editor_tab = ui.tab("Save Editor")
        db_tab = ui.tab("Database Inspector")

    with ui.tab_panels(tabs, value=editor_tab).classes("w-full"):
        with ui.tab_panel(editor_tab):
            with ui.card().classes("w-full"):
                components.render_editor(save, database)

        with ui.tab_panel(db_tab):
            # Todo: Implement this with:
            #   * A panel that confirms correcting mappings
            #   * A way to remap database entries
            ui.label("Placeholder!")

    ui.run(dark=None, native=True)
