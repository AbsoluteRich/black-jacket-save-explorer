from nicegui import ui

import data

if __name__ in {"__main__", "__mp_main__"}:
    save = data.Save()
    database = data.Database()

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

            with ui.card():
                with ui.grid(columns=6):
                    for current in range(len(save["DeckSave"]["GameCardSaves"])):
                        guid = save["DeckSave"]["GameCardSaves"][current][
                            "GameCardGuid"
                        ]
                        try:
                            group, suit_or_set, value = database.find(guid)  # type: ignore
                        except TypeError:
                            continue

                        match group:
                            case "awakened" | "blank":
                                if group == "blank" and suit_or_set != "death":
                                    ui.label(f"Blank {value} of {suit_or_set.title()}")
                                    continue

                                with (
                                    ui.image(
                                        f"https://blackjacket.wiki.gg/images/Card_{suit_or_set.title()}_{value}.png"
                                    )
                                    .classes("w-16")
                                    .on(
                                        "error",
                                        lambda: print(
                                            f"Failed https://blackjacket.wiki.gg/images/Card_{suit_or_set.title()}_{value}.png"
                                        ),
                                    )
                                ):
                                    with ui.context_menu():
                                        ui.menu_item("Set VFX")
                                        ui.menu_item("Replace")
                                        ui.menu_item("Remove")

                            case "face":
                                ui.label(value)

            ui.label("Artefacts")
            ui.label("Winner Pot Coins")
            ui.label("Stash Coins")
            ui.label("Seed")

            # ui.label("ChapterConfigGuid")
            # ui.label("SoulCoinGuid")
            # ui.label("NewDifficultyUnlocked")
            # ui.label("OpponentsWonAgainst")
            # ui.label("ObtainedSoulCoins")
            # ui.label("SuitGuids")
            # ui.label("CampaignPosition")
            # ui.label("StartsWithBoosterChoice")
            # ui.label("Bosses")
            # ui.label("RunGuid")
            # ui.label("Difficulty")
            # ui.label("CampaignPath")
            # ui.label("IsShopSave")
            # ui.label("ShopBossPhase")
            # ui.label("ShopSeed")
            # ui.label("ShopBurnAwakenActionsTaken")
            # ui.label("RandomSeed")
            # ui.label("RandomState")
            # ui.label("UsageTracker")
            # ui.label("SecondsPlayed")
            # ui.label("Version")
            # ui.label("IsDemoSave")
            # ui.label("references")

    ui.run(dark=None, native=True, reload=False)
