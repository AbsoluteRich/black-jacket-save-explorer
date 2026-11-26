from pathlib import Path

import platformdirs

# Todo: Support Xbox Game Pass saves


save_folder = (
    Path(platformdirs.user_data_dir() + "Low") / "Mipumi Games" / "BlackJacket"
)
game_save = Path(save_folder / "campaignSave.json")
database_file = Path.cwd() / "database.toml"

if not game_save.exists():
    raise FileNotFoundError("Game save not found!")

if not database_file.exists():
    raise FileNotFoundError("Database file not found!")
