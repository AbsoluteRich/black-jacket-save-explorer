from nicegui import ui

if __name__ in {"__main__", "__mp_main__"}:
    with ui.dialog().props("persistent") as dialog, ui.card():
        ui.label("Hello world!")
        ui.button("Close", on_click=dialog.close)

    dialog.open()

    ui.notify(
        "Unknown cards detected! Please declare them in the Data Collector.",
        type="warning",
    )

    with ui.tabs().classes("w-full") as tabs:
        collector = ui.tab("Data Collector")
        viewer = ui.tab("Deck Viewer")
        db = ui.tab("Known Cards")

    with ui.tab_panels(tabs, value=collector).classes("w-full"):
        with ui.tab_panel(collector):
            ui.linear_progress(0.5)
            ui.label("What card is this?")
            ui.radio(["Blank", "Awakened", "Face Card"]).props("inline")
            with ui.row():
                ui.input(
                    label="Suit",
                    placeholder="diamonds",
                )
                with ui.button(icon="info"):
                    ui.tooltip("Type all suit names in lower case with plurals.")
            ui.input(
                label="Value",
                placeholder="ace",
            )
            ui.button(
                "Continue",
                on_click=lambda: (
                    viewer.disable() if viewer.enabled else viewer.enable()
                ),
            )
        with ui.tab_panel(viewer):
            ui.label("Second tab")

            with ui.image(
                "https://blackjacket.wiki.gg/images/Card_Diamonds_2.png"
            ).classes("w-16"):
                with ui.context_menu():
                    ui.menu_item("Set VFX")
                    ui.menu_item("Replace")
                    ui.menu_item("Remove")
                    # ui.separator()
                    # ui.menu_item("Reset", auto_close=False)

    ui.run(dark=None, native=True, reload=False)
