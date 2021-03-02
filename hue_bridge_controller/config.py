import os
import toml

from pathlib import Path
from pydantic import BaseSettings

SETTINGS = None


class Settings(BaseSettings):
    username: str = "default_user"
    bridge_host: str = "localhost"


def load(config_file_name="pyproject.toml"):
    global SETTINGS
    if os.path.exists(config_file_name):
        config_string = Path(config_file_name).read_text()
        config_tmp = toml.loads(config_string)

        if "tool" in config_tmp and "hue" in config_tmp.get("tool", {}):
            SETTINGS = Settings(**config_tmp["tool"]["hue"])
            return

    SETTINGS = Settings()
