"""FastAPI application configuration model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic import ConfigDict

from giteaoauth.utils import FormatConverter


class AppConfig(BaseModel):
    """Application configuration model.

    Args:
        host (str): Hostname for the application server.
        port (int): Port number for the application server.
        log_level (Literal["debug", "info", "warning", "error"]):
            Logging level for the application.
    """

    model_config = ConfigDict(
        alias_generator=FormatConverter.snake_to_camel, populate_by_name=True
    )

    host: str = "localhost"
    port: int = 8000
    client_id: str = "84cd5c87-8426-4810-9c5e-9af3b9d5fa43"
    client_secret: str = (
        "gto_qmewvezwxyjqk7dfw7yryse5vnhv3qerz3yjdzsn45eeqtswrcja"
    )
    root_path: str = "/fastapi"
    log_level: Literal["debug", "info", "warning", "error"] = "info"

    @classmethod
    def from_json(cls, config_json: dict) -> AppConfig:
        """Create an AppConfig instance from a JSON dictionary."""
        config = AppConfig.model_validate(config_json)
        return config

    @classmethod
    def from_jsonfile(cls, config_file: str) -> AppConfig:
        """Create an AppConfig instance from a JSON file."""
        if not Path(config_file).exists():
            raise FileNotFoundError(
                f"Configuration file {config_file} not found."
            )
        with open(config_file, "r") as file:
            config_json = json.load(file)
        return cls.from_json(config_json)

    def to_jsonfile(self, config_file: str) -> None:
        """Save the AppConfig instance to a JSON file."""
        json_str = self.model_dump_json(indent=2, by_alias=True)
        with open(config_file, "w") as fout:
            fout.write(json_str)
