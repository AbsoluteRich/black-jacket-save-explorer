from nicegui import ui

import card_viewer
import config
import error_page


@ui.page("/")
def page() -> None:
    if config.check_paths():
        ui.navigate.to(card_viewer.page)
    else:
        ui.navigate.to(error_page.page)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(dark=None, native=True, reload=False)
