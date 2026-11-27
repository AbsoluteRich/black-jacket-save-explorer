from pathlib import Path

import platformdirs

game_save = (
    Path(platformdirs.user_data_dir() + "Low")
    / "Mipumi Games"
    / "BlackJacket"
    / "campaignSave.json"
)
database_file = Path.cwd() / "database.toml"


def check_paths() -> bool:
    return game_save.exists() and database_file.exists()
