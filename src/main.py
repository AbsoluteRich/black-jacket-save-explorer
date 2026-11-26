import mwcleric as mw
from nicegui import ui

import card_viewer
import data

if __name__ in {"__main__", "__mp_main__"}:
    # Setup
    save = data.Save()
    database = data.Database()
    wiki = mw.wikigg_client.Site("blackjacket.wiki.gg", path="/")

    # Initialise all UI elements
    ui.menu()
    lbl_cards = ui.label("Cards").classes("text-lg font-bold")

    # Card viewer
    with ui.card().classes("w-full"):
        btn_add = ui.button("Add")
        grd_cards = ui.grid(columns=6)

    # Artefacts
    lbl_artefacts = ui.label("Artefacts").classes("text-lg font-bold")
    with ui.card().classes("w-full"):
        ui.label("Placeholder!")

    # Footer
    with ui.footer().classes("bg-slate-900"):
        with ui.grid(columns=4).classes("size-full"):
            # Seed - changing it is unlikely to have useful results, so this is read only
            with ui.row().classes("items-center gap-2 no-wrap"):
                ui.label("Seed: ").classes("font-bold")
                lbl_seed = ui.label()

            # Stash coins
            with ui.row().classes("items-center gap-2 no-wrap"):
                ui.label("Stash Coins: ").classes("font-bold")
                num_stash = (
                    ui.number(min=0, value=0).props("dense dark").classes("w-20")
                )

            # Winner pot coins
            with ui.row().classes("items-center gap-2 no-wrap"):
                ui.label("Winner's Pot Coins: ").classes("font-bold")
                num_pot = ui.number(min=0, value=0).props("dense dark").classes("w-20")

            btn_edit = ui.button("Edit Other Values").props("dense")

    # Bind functionality to UI
    cv = card_viewer.CardViewer(save, database, wiki, lbl_cards, grd_cards)
    btn_add.on_click(cv.add_card)
    btn_edit.on_click(lambda: ui.notify("This feature is a work in progress!"))
    cv.render()

    lbl_seed.set_text(save["Seed"])

    num_stash.validation = num_pot.validation = {
        "Coins are over the cap. ALL of the excess coins will break if you gain new coins.": lambda x: x
        <= 15
    }

    # WARNING: Abstraction breaking occurs here
    num_stash.bind_value(save.data, "PlayerCoins").on_value_change(lambda: save.save())
    num_pot.bind_value(save.data, "WinnersPotCoins").on_value_change(
        lambda: save.save()
    )

    ui.run(dark=None, native=True, reload=False)
