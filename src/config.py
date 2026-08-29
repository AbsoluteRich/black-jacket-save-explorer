from pathlib import Path

import platformdirs

# To be updated to support Xbox Game Pass saves
SAVE_FOLDER = (
    Path(platformdirs.user_data_dir() + "Low") / "Mipumi Games" / "BlackJacket"
)
GAME_SAVE = Path(SAVE_FOLDER / "campaignSave.json")
DATABASE_FILE = Path.cwd() / "database.toml"
