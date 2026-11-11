from pathlib import Path

import platformdirs

# Todo: Support Xbox Game Pass saves
SAVE_FOLDER = (
    Path(platformdirs.user_data_dir() + "Low") / "Mipumi Games" / "BlackJacket"
)
GAME_SAVE = Path(SAVE_FOLDER / "campaignSave.json")
DATABASE_FILE = Path.cwd() / "database.toml"

if not GAME_SAVE.exists():
    raise FileNotFoundError("Game save not found!")

if not DATABASE_FILE.exists():
    raise FileNotFoundError("Database file not found!")
