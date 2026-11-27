import atexit
import dataclasses
import json
import os
import tempfile
from collections.abc import Callable, Coroutine
from pathlib import Path

import tomlkit as toml
import tomlkit.exceptions
from nicegui import ui
from nicegui.elements.button import Button
from nicegui.elements.label import Label
from nicegui.elements.spinner import Spinner
from nicegui.elements.upload import Upload
from nicegui.events import ClickEventArguments, UploadEventArguments

import config
import main


@dataclasses.dataclass()
class Sector:
    readable_name: str
    path: Path
    html_description: str
    callback: Callable[
        [UploadEventArguments], Coroutine[None, None, tuple[bool, str | None]]
    ]


def reload_page(_: ClickEventArguments, btn: Button, spn: Spinner, lbl: Label) -> None:
    btn.set_enabled(False)
    spn.set_visibility(True)
    lbl.set_visibility(True)
    main.page()  # Confusing, eh?


def test_data(
        obj: dict, valid_keys: tuple[str, ...], data_type: str
) -> tuple[bool, str | None]:
    if all(key in obj for key in valid_keys):
        return True, data_type
    else:
        return False, "Invalid file structure!"


async def test_save(f: UploadEventArguments) -> tuple[bool, str | None]:
    try:
        potential_file: dict = json.loads(await f.file.read())
        return test_data(
            potential_file,
            ("DeckSave", "WinnersPotCoins", "PlayerCoins", "Seed"),
            "save",
        )
    except json.JSONDecodeError:
        return False, "Not a JSON file!"


async def test_database(f: UploadEventArguments) -> tuple[bool, str | None]:
    try:
        potential_file: dict = toml.loads(await f.file.read())
        return test_data(potential_file, ("cards", "artefacts"), "database")
    except toml.exceptions.ParseError:
        return False, "Not a TOML file!"


async def handle_test(
        args: UploadEventArguments,
        upl: Upload,
        callback: Callable[
            [UploadEventArguments], Coroutine[None, None, tuple[bool, str | None]]
        ],
) -> None:
    # The reload button isn't disabled, because if you click it before this function is ready you'll just get booted
    # back to this page
    res, message_or_type = await callback(args)

    if res:
        upl.props("color=green")
        upl.set_label("Valid.")
        upl.set_enabled(False)

        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as f:
            f.write(await args.file.read())
            f.flush()

            # Scary!! The variable MUST point to a temporary file at this point
            # Todo: You are a FUCKING IDIOT WHY WOULD YOU DELETE THE TEMP FILE IF YOU WRITE TO IT?? MOVE THE FILE TO THE
            #       CWD AFTER YOU'RE DONE
            if message_or_type == "save":
                config.game_save = tempfile.gettempdir() / Path(f.name)
                atexit.register(os.remove, config.game_save)
            elif message_or_type == "database":
                config.database_file = tempfile.gettempdir() / Path(f.name)
                atexit.register(os.remove, config.database_file)
    else:
        upl.props("color=red")
        upl.set_label(message_or_type)


@ui.page("/error")
def page() -> None:
    sectors = [
        Sector(
            "game save",
            config.game_save,
            "Save file not found. PLACEHOLDER INSTRUCTIONS",
            # If you've installed the game with Xbox Game Pass, you may need to find your files in a different location
            # - use these steps.
            # <ul class='list-decimal list-inside'>
            #   <li>Step 1: Press Windows + R</li>
            #   <li>Step 2: ???</li>
            #   <li>Step 3: Profit</li>
            # </ul>
            test_save,
        ),
        Sector(
            "database",
            config.database_file,
            "Database file not found. Get the latest version from <a "
            "href='https://github.com/AbsoluteRich/black-jacket-save-explorer/blob/main/src/database.toml' "
            "target='_blank' class='text-blue-500 hover:underline'>the GitHub repo</a>.",
            test_database,
        ),
    ]

    with ui.grid(columns=2).classes("size-full"):
        for sector in sectors:
            with ui.card().classes("w-full") as card:
                if sector.path.exists():
                    card.classes("justify-center items-center")
                    ui.icon("done", size="500%")
                    ui.label(f"No action needed for {sector.readable_name}.")
                else:
                    # NiceGUI can't embed links in text...
                    # Turning off sanitisation, because otherwise the target param will get stripped
                    ui.html(sector.html_description, sanitize=False)

                    # upl_file doesn't exist until the end of the function, so we avoid the parameter and use a function
                    # to bind the upload callback
                    upl_file = ui.upload(max_files=1, auto_upload=True).classes(
                        "w-full"
                    )
                    upl_file.on_upload(
                        lambda f, u=upl_file, cb=sector.callback: handle_test(f, u, cb)
                    )

    with ui.row().classes("gap-2 align-middle"):
        btn_loader = ui.button("Reload")
        spn_loader = ui.spinner().set_visibility(False)
        lbl_loader = ui.label("Reloading...").set_visibility(False)
        btn_loader.on_click(
            lambda _: reload_page(_, btn_loader, spn_loader, lbl_loader)
        )
